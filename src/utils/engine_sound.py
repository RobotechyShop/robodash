"""
Engine sound synthesizer for mock mode.

Generates realistic 2JZ-GTE engine sounds based on RPM.
Uses pygame.mixer for audio playback and numpy for sound synthesis.

The sound is synthesized using multiple harmonics to simulate
the characteristic inline-6 exhaust note.
"""

import logging
import math
from typing import Optional
import threading

logger = logging.getLogger(__name__)

# Audio parameters
SAMPLE_RATE = 44100
BUFFER_SIZE = 2048

# Try to import pygame and numpy
try:
    import pygame
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    logger.warning("pygame or numpy not available - engine sound disabled")


class EngineSoundSynthesizer:
    """
    Real-time engine sound synthesizer.

    Generates a continuous engine sound that varies with RPM.
    Uses multiple harmonics to simulate a 6-cylinder engine.

    The 2JZ-GTE has a characteristic smooth inline-6 sound with
    a relatively high-pitched exhaust note under boost.
    """

    # 2JZ-GTE characteristics
    CYLINDERS = 6
    IDLE_RPM = 850
    REDLINE_RPM = 7200

    def __init__(self, volume: float = 0.5):
        """
        Initialize the engine sound synthesizer.

        Args:
            volume: Master volume (0.0 to 1.0)
        """
        self._enabled = False
        self._running = False
        self._rpm = self.IDLE_RPM
        self._target_rpm = self.IDLE_RPM
        self._volume = max(0.0, min(1.0, volume))
        self._phase = 0.0
        self._lock = threading.Lock()
        self._channel: Optional["pygame.mixer.Channel"] = None

        if not AUDIO_AVAILABLE:
            logger.warning("Audio not available - sound synthesis disabled")
            return

        try:
            # Initialize pygame mixer
            pygame.mixer.pre_init(
                frequency=SAMPLE_RATE,
                size=-16,  # 16-bit signed
                channels=1,  # Mono
                buffer=BUFFER_SIZE
            )
            pygame.mixer.init()
            self._enabled = True
            logger.info("Engine sound synthesizer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize audio: {e}")
            self._enabled = False

    def start(self) -> None:
        """Start engine sound playback."""
        if not self._enabled:
            return

        self._running = True
        self._phase = 0.0

        # Start the sound generation thread
        self._audio_thread = threading.Thread(
            target=self._audio_loop,
            daemon=True
        )
        self._audio_thread.start()
        logger.info("Engine sound started")

    def stop(self) -> None:
        """Stop engine sound playback."""
        self._running = False
        if self._channel:
            self._channel.stop()
        logger.info("Engine sound stopped")

    def set_rpm(self, rpm: float) -> None:
        """
        Update the engine RPM for sound synthesis.

        Args:
            rpm: Current engine RPM
        """
        with self._lock:
            self._target_rpm = max(self.IDLE_RPM, min(self.REDLINE_RPM, rpm))

    def set_volume(self, volume: float) -> None:
        """
        Set the master volume.

        Args:
            volume: Volume level (0.0 to 1.0)
        """
        self._volume = max(0.0, min(1.0, volume))

    def play_gear_change(self, upshift: bool = True) -> None:
        """
        Play a gear change sound effect.

        Args:
            upshift: True for upshift, False for downshift.
        """
        if not self._enabled or not AUDIO_AVAILABLE:
            return

        try:
            # Generate gear change sound
            duration = 0.15 if upshift else 0.2
            num_samples = int(SAMPLE_RATE * duration)
            t = np.arange(num_samples) / SAMPLE_RATE

            if upshift:
                # Upshift: quick "clunk" + brief silence (gear cut)
                # Mechanical clunk sound
                clunk_freq = 150
                clunk = np.sin(2 * np.pi * clunk_freq * t) * np.exp(-t * 30)

                # Add metallic character
                metal = np.sin(2 * np.pi * 800 * t) * np.exp(-t * 50) * 0.3
                metal += np.sin(2 * np.pi * 1200 * t) * np.exp(-t * 60) * 0.2

                samples = clunk + metal
            else:
                # Downshift: blip/rev sound
                freq_start = 200
                freq_end = 350
                freq = freq_start + (freq_end - freq_start) * t / duration
                blip = np.sin(2 * np.pi * freq * t) * np.exp(-t * 15)

                samples = blip * 0.8

            # Normalize
            max_val = np.max(np.abs(samples))
            if max_val > 0:
                samples = samples / max_val * 0.7

            # Convert and play
            sound_array = (samples * 32767 * self._volume).astype(np.int16)
            sound = pygame.sndarray.make_sound(sound_array)
            sound.play()

        except Exception as e:
            logger.error(f"Failed to play gear change sound: {e}")

    def _audio_loop(self) -> None:
        """Main audio generation loop (runs in thread)."""
        if not AUDIO_AVAILABLE:
            return

        while self._running:
            try:
                # Generate audio buffer
                samples = self._generate_samples(BUFFER_SIZE)

                # Convert to pygame Sound
                sound_array = (samples * 32767 * self._volume).astype(np.int16)
                sound = pygame.sndarray.make_sound(sound_array)

                # Play and wait for completion
                channel = sound.play()
                if channel:
                    while channel.get_busy() and self._running:
                        pygame.time.wait(5)

            except Exception as e:
                logger.error(f"Audio generation error: {e}")
                break

    def _generate_samples(self, num_samples: int) -> "np.ndarray":
        """
        Generate audio samples based on current RPM.

        Uses harmonics to create a realistic engine sound:
        - Base frequency from firing rate
        - 2nd, 3rd, 4th harmonics for richness
        - Amplitude modulation for "burble" effect

        Args:
            num_samples: Number of samples to generate

        Returns:
            numpy array of audio samples (-1.0 to 1.0)
        """
        if not AUDIO_AVAILABLE:
            return np.zeros(num_samples)

        # Smooth RPM transition
        with self._lock:
            target = self._target_rpm

        # Interpolate RPM for smooth sound changes
        rpm_smoothing = 0.1
        self._rpm = self._rpm + (target - self._rpm) * rpm_smoothing

        # Calculate base frequency
        # For a 6-cylinder 4-stroke: 3 firing events per revolution
        # Frequency = (RPM / 60) * 3
        base_freq = (self._rpm / 60.0) * (self.CYLINDERS / 2)

        # Time array for this buffer
        t = np.arange(num_samples) / SAMPLE_RATE

        # Advance phase to maintain continuity between buffers
        t = t + self._phase

        # Generate harmonics
        samples = np.zeros(num_samples, dtype=np.float32)

        # Harmonic amplitudes (tuned for meaty 2JZ-GTE turbo sound)
        # More bass, deeper exhaust note
        harmonics = [
            (0.25, 0.5),   # Deep sub-bass
            (0.5, 0.7),    # Sub-harmonic for low-end rumble
            (1.0, 1.0),    # Fundamental
            (1.5, 0.4),    # Between fundamental and 2nd
            (2.0, 0.5),    # 2nd harmonic
            (3.0, 0.25),   # 3rd harmonic
            (4.0, 0.15),   # 4th harmonic
            (6.0, 0.1),    # Higher overtone
        ]

        for harmonic_mult, amplitude in harmonics:
            freq = base_freq * harmonic_mult
            # Use slightly distorted sine for more aggressive sound
            wave = np.sin(2 * np.pi * freq * t)
            # Soft clipping for some distortion/saturation
            wave = np.tanh(wave * 1.5) * 0.8
            samples += amplitude * wave

        # Add some "growl" - amplitude modulation at cam frequency
        cam_freq = self._rpm / 120.0  # Camshaft frequency
        am_depth = 0.2 + (self._rpm - self.IDLE_RPM) / self.REDLINE_RPM * 0.15
        am = 1.0 - am_depth * (np.sin(2 * np.pi * cam_freq * t) ** 2)
        samples *= am

        # Add turbo whoosh at higher RPM
        rpm_factor = max(0, (self._rpm - self.IDLE_RPM) / (self.REDLINE_RPM - self.IDLE_RPM))
        if rpm_factor > 0.3:
            turbo_freq = 80 + rpm_factor * 120  # Turbo whine
            turbo_wave = np.sin(2 * np.pi * turbo_freq * t) * 0.15 * (rpm_factor - 0.3)
            samples += turbo_wave

        # Add some noise/crackle - more at higher RPM
        noise_level = 0.03 + rpm_factor * 0.12
        samples += np.random.uniform(-noise_level, noise_level, num_samples)

        # Exhaust pops at lower RPM (decel)
        if rpm_factor < 0.3:
            pop_chance = 0.002
            if np.random.random() < pop_chance:
                pop = np.exp(-np.arange(num_samples) / 100) * 0.3
                samples += pop * np.random.choice([-1, 1])

        # Volume increases with RPM (like real engine)
        rpm_volume = 0.6 + rpm_factor * 0.4
        samples *= rpm_volume

        # Normalize
        max_val = np.max(np.abs(samples))
        if max_val > 0:
            samples = samples / max_val * 0.9

        # Update phase for continuity
        self._phase = (self._phase + num_samples / SAMPLE_RATE) % 1.0

        return samples

    @property
    def is_enabled(self) -> bool:
        """Check if audio is available and initialized."""
        return self._enabled

    @property
    def is_running(self) -> bool:
        """Check if sound is currently playing."""
        return self._running


def create_engine_sound(volume: float = 0.5) -> Optional[EngineSoundSynthesizer]:
    """
    Factory function to create engine sound synthesizer.

    Returns None if audio is not available.

    Args:
        volume: Initial volume (0.0 to 1.0)

    Returns:
        EngineSoundSynthesizer instance or None
    """
    if not AUDIO_AVAILABLE:
        return None

    synth = EngineSoundSynthesizer(volume)
    return synth if synth.is_enabled else None
