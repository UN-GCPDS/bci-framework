"""
===========================================
Visuospatial Working Memory - Neurofeedback
===========================================


"""

import logging
from typing import Literal, TypeVar

from bci_framework.extensions.stimuli_delivery import StimuliAPI, Feedback, DeliveryInstance
from bci_framework.extensions.stimuli_delivery.utils import Widgets as w
from bci_framework.extensions import properties as prop

from browser import document, html, timer

Ts = TypeVar('Time in seconds')
Tm = TypeVar('Time in milliseconds')
TM = TypeVar('Time in minutes')


########################################################################
class VWMNeurofeedback(StimuliAPI):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_stylesheet('styles.css')

        self.show_cross()
        self.show_synchronizer()

        self.feedback = Feedback(self, 'VisualWorkingMemory')
        self.feedback.on_feedback(self.on_input_feedback)

        self.bci_stimuli <= html.DIV(id='stimuli')

        self.dashboard <= w.label(
            'Visuospatial working memory - Neurofeedback', 'headline4')
        self.dashboard <= html.BR()

        self.dashboard <= w.subject_information(
            paradigm='Visuospatial working memory - Neurofeedback')

        self.dashboard <= w.slider(
            label='Baseline acquisition:',
            min=1,
            value=1,
            max=5,
            step=0.1,
            unit='m',
            id='baseline_duration',
        )
        self.dashboard <= w.slider(
            label='Sesion duration:',
            min=5,
            value=10,
            max=30,
            step=0.1,
            unit='m',
            id='sesion_duration',
        )

        self.dashboard <= w.slider(
            label='Window analysis:',
            min=0.5,
            max=2,
            value=1,
            step=0.1,
            unit='s',
            id='window_analysis',
        )

        self.dashboard <= w.slider(
            label='Sliding data:',
            min=0.1,
            max=2,
            value=1,
            unit='s',
            step=0.1,
            id='sliding_data',
        )

        self.dashboard <= w.select(
            'Analysis Function',
            [['kTE PAC', 'kTE PAC'], ['CFD', 'CFD'], ['AlphaFz', 'AlphaFz']],
            value='kTE PAC',
            id='analysis_function',
        )

        self.dashboard <= w.switch(
            label='Record EEG',
            checked=False,
            id='record',
        )

        self.dashboard <= w.toggle_button(
            [('Start session', self.start), ('Stop session', self.stop_session)], id='run')

        self.dashboard <= w.slider(
            label='Test feedback:',
            min=-1,
            max=1,
            value=0,
            step=0.1,
            id='test',
            on_change=self.test_feedback,
        )

    # ----------------------------------------------------------------------
    @DeliveryInstance.both
    def test_feedback(self, value):
        """Test the feedback stimuli."""
        self.on_input_feedback(**{'feedback': value, })

    # ----------------------------------------------------------------------
    def on_input_feedback(self, **feedback: dict[str, [str, int]]) -> None:
        """Asynchronous method to receive the feedback process value.

        `feedback` is a dictionary with the keys:

          * `feedback`: The feedback value, an `int` between -1 and 1.
          * `baseline`: The baseline value freezed.
        """

        f = feedback['feedback']
        self.send_marker(f'{f}')
        fp = self.map(f, -1, 1, 0, 100)

        document.select_one('#stimuli').style = {
            'background-position-x': f'{fp}%',
            'display': 'block'
        }

    # ----------------------------------------------------------------------
    def start(self) -> None:
        """Start the session.

        A session comprises a baseline calculation and a neurofeedback trial.
        """
        if w.get_value('record'):
            self.start_record()

        self.build_trials()
        self.show_counter(5)
        timer.set_timeout(self.start_session, 5000)

    # ----------------------------------------------------------------------
    def start_session(self) -> None:
        """Execute the session pipeline."""
        self.run_pipeline(self.pipeline_trial,
                          self.trials, callback='stop_run')

    # ----------------------------------------------------------------------
    def stop_session(self) -> None:
        """Stop pipeline execution."""
        document.select_one('#stimuli').style = {'display': 'none'}
        self.stop_analyser()
        w.get_value('run').off()
        if w.get_value('record'):
            timer.set_timeout(self.stop_record, 2000)

    # ----------------------------------------------------------------------
    def build_trials(self) -> None:
        """Define the session and single session pipeline."""

        baseline_duration = w.get_value('baseline_duration') * 60
        sesion_duration = w.get_value('sesion_duration') * 60
        baseline_packages = baseline_duration // w.get_value('sliding_data')

        logging.warning(f'BP: {baseline_packages}')

        self.trials = [{
            'function': w.get_value('analysis_function'),
            'window_analysis': w.get_value('window_analysis'),
            'sliding_data': w.get_value('sliding_data') * prop.SAMPLE_RATE,
            'baseline_packages': baseline_packages,
        }]

        self.pipeline_trial = [
            ['configure_analyser', 1000],
            ['baseline', baseline_duration * 1000],
            ['session', sesion_duration * 1000],
            ['stop_analyser', 1000],
        ]

    # ----------------------------------------------------------------------
    def configure_analyser(self, function: Literal['kTE PAC', 'CFD', 'AlphaFz'],
                           window_analysis: Ts,
                           sliding_data: int,
                           baseline_packages: int) -> None:
        """Send the configuration values to the generator."""

        data = {
            'status': 'on',
            'function': function,
            'window_analysis': window_analysis,
            'sliding_data': sliding_data,
            'baseline_packages': baseline_packages,
            'channels': list(prop.CHANNELS.values()),
            'sample_rate': int(prop.SAMPLE_RATE),
        }
        logging.warning(f'CONFIG: {data}')
        self.feedback.write(data)

    # ----------------------------------------------------------------------
    def baseline(self) -> None:
        """Acquire data to use in the zero location."""

        self.show_cross()
        self.send_marker('Start baseline')
        document.select_one('#stimuli').style = {'display': 'none'}

    # ----------------------------------------------------------------------
    def session(self) -> None:
        """Neurofeedback activity."""

        self.send_marker('End baseline')
        self.feedback.write({'command': 'freeze_baseline'})  # zero location
        document.select_one('#stimuli').style = {'display': 'block'}

    # ----------------------------------------------------------------------
    def stop_analyser(self) -> None:
        """Stop feedback values generation."""
        self.feedback.write({
            'status': 'off',
        })


if __name__ == '__main__':
    VWMNeurofeedback()


