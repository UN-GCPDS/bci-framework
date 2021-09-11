from mdc.MDCComponent import MDCComponent
from mdc.MDCButton import MDCButton
from mdc.MDCFormField import MDCFormField, MDCCheckbox, MDCForm
from mdc.MDCLinearProgress import MDCLinearProgress

from browser import document, html, timer


########################################################################
class Widgets:

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        self.widgets = {}
        self.component = {}

    # ----------------------------------------------------------------------
    def _fix_value(self, value):
        """"""
        if isinstance(value, int):
            return value
        elif isinstance(value, float) and value.is_integer():
            return int(value)
        elif isinstance(value, float):
            return round(value, 2)
        elif isinstance(value, str):
            return value
        else:
            return value

    # ----------------------------------------------------------------------
    def _round(self, v):
        """"""
        if v == int(v):
            return int(v)
        return float(v)

    # ----------------------------------------------------------------------
    def get_value(self, id):
        """"""
        v = self.widgets.get(id)
        if isinstance(v, (list, tuple)):
            return list(map(self._fix_value, v))
        else:
            return self._fix_value(v)

    # ----------------------------------------------------------------------
    def __getitem__(self, id):
        """"""
        return self.get_value(id)

    # ----------------------------------------------------------------------
    def label(self, text, typo='body1', style={}, id=None, *args, **kwargs):
        """"""
        label = MDCComponent(html.SPAN(f'{text}'), id=id, style={
                             **style, **{'width': '100%', 'display': 'flex'}}, *args, **kwargs)
        label.mdc.typography(typo)

        if id:
            self.component[id] = label

        return label

    # ----------------------------------------------------------------------
    def slider(self, label, min, max, value, step=1, unit='', marks=False, on_change=None, id=None, *args, **kwargs):
        """"""
        form = MDCForm()
        label_ = MDCComponent(html.SPAN(f'{label}'))
        label_ .mdc.typography('subtitle1')
        form <= label_
        form <= MDCComponent(html.SPAN(
            f' {self._round(value)} {unit}', id=f'value_{id}')).mdc.typography('caption')
        slider_ = form.mdc.Slider(
            'Slider', min=min, max=max, value=value, step=step, marks=marks, *args, **kwargs)

        if on_change:
            slider_.mdc.listen('MDCSlider:change',
                               lambda evt: on_change(self.widgets[id]))

        if id:
            self.widgets[id] = self._fix_value(value)
            self.component[id] = slider_

            def set_value(id, value):
                self.widgets[id] = self._round(value)
                document.select_one(
                    f'#value_{id}').html = f' {self.get_value(id)} {unit}'

            slider_.mdc.listen('MDCSlider:input', lambda event: set_value(
                id, slider_.mdc.getValue()))

        return form

    # ----------------------------------------------------------------------
    def range_slider(self, label, min, max, value_lower, value_upper, step, unit='', on_change=None, id=None, *args, **kwargs):
        """"""
        form = MDCForm()
        label_ = MDCComponent(html.SPAN(f'{label}'))
        label_ .mdc.typography('subtitle1')
        form <= label_
        form <= MDCComponent(html.SPAN(
            f' {self._round(value_lower)}-{self._round(value_upper)} {unit}', id=f'value_{id}')).mdc.typography('caption')
        slider_ = form.mdc.RangeSlider(
            'Slider', min, max, value_lower, value_upper, step, *args, **kwargs)

        if on_change:
            slider_.mdc.listen('MDCSlider:change',
                               lambda evt: on_change(self.widgets[id]))

        if id:
            self.widgets[id] = [self._fix_value(
                value_lower), self._fix_value(value_upper)]
            self.component[id] = slider_

            def set_value(id, value):
                self.widgets[id] = [self._round(
                    value[0]), self._round(value[1])]
                document.select_one(
                    f'#value_{id}').html = f' {self.get_value(id)[0]}-{self.get_value(id)[1]} {unit}'

            slider_.mdc.listen('MDCSlider:input', lambda event: set_value(
                id, [slider_.mdc.getValueStart(), slider_.mdc.getValue()]))

        return form

    # ----------------------------------------------------------------------
    def radios(self, label, options, on_change=None, id=None):
        """"""
        label = MDCComponent(html.SPAN(f'{label}'))
        label.mdc.typography('subtitle1')
        radios_ = []
        form = MDCForm(formfield_style={'width': '100px'})
        form <= label

        for i, (radio, value) in enumerate(options):
            radios_.append(
                [form.mdc.Radio(radio, name=id, checked=(i == 0)), value])

        if id:
            self.widgets[id] = options[0][1]
            self.component[id] = radios_

            def set_value(value):
                def wrap(evt):
                    self.widgets[id] = value
                return wrap

            for radio, value in radios_:
                radio.bind('change', set_value(value))

        if on_change:
            for radio, _ in radios_:
                radio.bind('change', lambda evt: on_change())

        return form

    # ----------------------------------------------------------------------
    def checkbox(self, label, options, on_change=None, id=None):
        """"""
        label = MDCComponent(html.SPAN(f'{label}'),
                             style={'flex-basis': '100%'})
        label.mdc.typography('subtitle1')
        checkbox_ = []
        form = MDCForm(formfield_style={
            'min-width': 'unset',
            'width': 'unset',
            # 'display': 'inline',
            # 'vertical-align': 'super',
        })
        form <= label
        form <= html.BR()

        for checkbox, checked in options:
            checkbox_.append(
                [form.mdc.Checkbox(checkbox, name=id, checked=checked), checkbox])

        if id:
            self.widgets[id] = [ch[0] for ch in options if ch[1]]
            self.component[id] = checkbox_

            def set_value():
                def wrap(evt):
                    self.widgets[id] = [value for ch,
                                        value in checkbox_ if ch.mdc.checked]
                return wrap

            for checkbox, _ in checkbox_:
                checkbox.bind('change', set_value())

        if on_change:
            for checkbox, _ in checkbox_:
                checkbox.bind('change', lambda evt: on_change())

        return form

    # ----------------------------------------------------------------------
    def select(self, label, options, value=None, on_change=None, id=None, hide_label=False):
        """"""
        label_ = MDCComponent(html.SPAN(f'{label}'))
        label_ .mdc.typography('subtitle1')
        form = MDCForm(formfield_style={
                       'width': '100px', 'min-height': '90px', 'margin-left': '15px'})
        if not hide_label:
            form <= label_

        select_ = form.mdc.Select('', options=options, selected=value, id=id)

        if id:
            self.widgets[id] = value
            self.component[id] = select_

            def set_value():
                def wrap(evt):
                    self.widgets[id] = select_.mdc.value
                return wrap

            select_.mdc.listen('MDCSelect:change', set_value())

        if on_change:
            select_.mdc.listen('MDCSelect:change',
                               lambda evt: on_change(select_.mdc.value))

        return form

    # ----------------------------------------------------------------------
    def button(self, label, unelevated=True, on_click=None, style={}, id=None, *args, **kwargs):
        """"""
        btn = MDCButton(label, unelevated=unelevated,
                        style=style, id=id, *args, **kwargs)

        if on_click:
            btn.bind('click', lambda evt: on_click())

        if id:
            self.component[id] = btn

        return btn

    # ----------------------------------------------------------------------
    def toggle_button(self, buttons, style={}, id='', *args, **kwargs):
        """"""
        def toggle(btn1, btn2):
            document.select_one(f'#{btn1}').style = {'display': 'none'}
            document.select_one(f'#{btn2}').style = {
                'display': 'inline-flex'}
            document.select_one(f'#{btn2}').disabled = True
            timer.set_timeout(lambda: setattr(document.select_one(
                f'#{btn2}'), 'disabled', False), 1000)

        def on_btn1():
            buttons[0][1]()
            toggle(f'{id}-btnt1', f'{id}-btnt2')

        def on_btn2():
            buttons[1][1]()
            toggle(f'{id}-btnt2', f'{id}-btnt1')

        style1 = style
        style2 = style.copy()
        style2.update({'background-color': '#da4453', 'display': 'none'})

        area = html.DIV()
        area <= self.button(
            buttons[0][0], id=f'{id}-btnt1', style=style1, on_click=on_btn1, *args, **kwargs)
        area <= self.button(
            buttons[1][0], id=f'{id}-btnt2', style=style2, on_click=on_btn2, *args, **kwargs)

        area.on = lambda: toggle(f'{id}-btnt1', f'{id}-btnt2')
        area.off = lambda: toggle(f'{id}-btnt2', f'{id}-btnt1')

        self.widgets[id] = area
        return area

    # ----------------------------------------------------------------------
    def switch(self, label, checked=False, on_change=None, id=None):
        """"""
        form = MDCForm(formfield_style={'width': '100%', 'height': '40px'})
        switch_ = form.mdc.Switch(label, checked)
        form.select_one('label').style = {'margin-left': '10px'}

        if on_change:
            switch_.bind('change', lambda *args,
                         ** kwargs: on_change(switch_.mdc.checked))

        if id:
            self.widgets[id] = checked
            self.component[id] = switch_

            def set_value():
                def wrap(evt):
                    self.widgets[id] = switch_.mdc.checked
                return wrap

            switch_.bind('change', set_value())

        return form
