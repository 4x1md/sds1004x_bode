"""Minimalist driver for FYXXXX signal generators.

  For a full-featured implementation of all AWG features, see:
    https://github.com/mattwach/fygen
"""

import serial
import time

import exceptions
from base_awg import BaseAWG

AWG_ID = "fy"
AWG_OUTPUT_IMPEDANCE = 50.0
MAX_READ_SIZE = 256
RETRY_COUNT = 2
VERBOSE = False  # Set to True for protocol debugging 

def debug(msg, *args):
    if VERBOSE:
        print(msg % args)

class FygenAWG(BaseAWG):
    """Driver API."""

    SHORT_NAME = "fy"

    def __init__(self, port, baud_rate=115200, timeout=5):
        self.fy = None
        self.port = None
        self.serial_path = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        # None -> Hi-Z
        self.load_impedance = {
                1: None,
                2: None,
        }

    def connect(self):
        if self.port:
          return

        self.port = serial.Serial(
            port=self.serial_path,
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            rtscts=False,
            dsrdtr=False,
            xonxoff=False,
            timeout=self.timeout)

        debug("Connected to %s", self.serial_path)
        self.port.reset_output_buffer()
        self.port.reset_input_buffer()

    def disconnect(self):
        if self.port:
            debug("Disconnected from %s", self.serial_path)
            self.port.close()
            self.port = None

    def initialize(self):
        self.connect()
        self.enable_output(0, False)

    def get_id(self):
        return AWG_ID

    def enable_output(self, channel, on):
        """Turns a channel on (True) or off (False)."""
        self._retry(
            channel,
            "N",
            "1" if on else "0",
            "255" if on else "0") 

    def set_frequency(self, channel, freq):
        """Sets frequency for a channel.

          freq is a floating point value in Hz.
        """
        uhz = int(freq * 1000000.0)

        # AWG Bug: With the FY2300 and some values of frequency (for example
        # 454.07 Hz) a bug occurs where the UI of the generator shows the
        # correct value on the UI but the "RMF" command returns an incorrect
        # fractional hertz value (454.004464 Hz for the example above).
        # The work-around is to just match the Hz part of the return
        # value.
        def match_hz_only(match, got):
          if '.' in got and match == got[:got.index('.')]:
              return True
          debug('set_frequency mismatch (looking at Hz value only)')
          return False

        self._retry(
            channel,
            "F",
            "%014u" % uhz,
            "%08u" % int(freq),
            match_fn=match_hz_only)

    def set_phase(self, phase):
        """Sets the phase of a channel in degrees."""
        self._retry(
            2,  # always channel 2 (not sure why)
            "P",
            "%.3f" % phase,
            "%u" % (phase * 1000))

    def set_wave_type(self, channel, wvtp):
        """Sets a channel to a sin wave."""
        del wvtp  # This parameter is ignored, always set a sin wave
        self._retry(channel, "W", "0", "0")

    def set_amplitue(self, channel, amp):
        """Sets a channel amplitude in volts.

          Load impedeance for the channel is taken into account
          when calculating the amplitude.  For example, if the load
          impedance is 50 ohms and amp=50 ohms, the actual voltage
          set is 1 * (50 + 50) / 50 = 2V.
        """
        volts = round(self._apply_load_impedance(channel, amp), 4)
        self._retry(
            channel,
            "A",
            "%.4f" % volts,
            "%u" % (volts * 10000))

    def set_offset(self, channel, offset):
        """Sets the voltage offset for a channel.

          offset is a floating point number.
        """
        # Factor in load impedance.
        offset = self._apply_load_impedance(channel, offset)

        # AWG Bug: The FY2300 returns negative offsets as
        # an unsigned integer.  Thus math is needed to predict
        # the returned value correctly
        offset_unsigned = int(round(offset, 3) * 1000.0)
        if offset_unsigned < 0:
          offset_unsigned = 0x100000000 + offset_unsigned
        self._retry(
            channel,
            "O",
            "%.3f" % offset,
            "%u" % offset_unsigned)

    def set_load_impedance(self, channel, z):
        """Sets the load impedance for a channel."""
        maxz = 10000000.0
        if z > maxz:
            z = None  # Hi-z
        self.load_impedance[channel] = z

    def _apply_load_impedance(self, channel, volts):
        if channel not in self.load_impedance:
          raise exceptions.UnknownChannelError("Unknown channel: %s" % channel)
        if not self.load_impedance[channel]:
          return volts  # Hi-Z
        loadz = self.load_impedance[channel]
        return volts * (AWG_OUTPUT_IMPEDANCE + loadz) / loadz

    def _recv(self, command):
        """Waits for device."""
        response = self.port.read_until(size=MAX_READ_SIZE).decode("utf8")
        debug("%s -> %s", command.strip(), response.strip())
        return response

    def _send(self, command, retry_count=5):
        """Sends a low-level command. Returns the response."""
        debug("send (attempt %u/5) -> %s", 6 - retry_count, command)

        data = command + "\n"
        data = data.encode()
        self.port.reset_output_buffer()
        self.port.reset_input_buffer()
        self.port.write(data)
        self.port.flush()

        response = self._recv(command)

        if not response and retry_count > 0:
            # sometime the siggen answers queries with nothing.  Wait a bit,
            # then try again
            time.sleep(0.1)
            return self._send(command, retry_count - 1)

        return response.strip()

    def _retry(self, channel, command, value, match, match_fn=None):
        """Retries the command until match is satisfied."""
        if channel == 0:
          self._retry(1, command, value, match)
          self._retry(2, command, value, match)
          return
        elif channel == 1:
            channel = "M"
        elif channel == 2:
            channel = "F"
        else:
            raise exceptions.UnknownChannelError("Channel shoud be 1 or 2")

        if not match_fn:
          # usually we want ==
          match_fn = lambda match, got: match == got

        if match_fn(match, self._send("R" + channel + command)):
            debug("already set %s", match)
            return

        for _ in range(RETRY_COUNT):
            self._send("W" + channel + command + value)
            if match_fn(match, self._send("R" + channel + command)):
                debug("matched %s", match)
                return
            debug("mismatched %s", match)

        # Print a warning.  This is not an error because the AWG read bugs
        # worked-around in this module could vary by AWG model number or
        # firmware revision number.
        sys.stderr.write(
              "Warning: %s did not produce an expected response after %d "
              "retries\n" % (
                  "W" + channel + command + value, RETRY_COUNT))

if __name__ == '__main__':
    print "This module shouldn't be run. Run awg_tests.py instead."
