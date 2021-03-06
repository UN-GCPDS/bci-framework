# from mdc import MDCButton, MDCCheckbox, MDCFormField, MDCForm, MDCComponent, MDCLinearProgress
from mdc.MDCComponent import MDCComponent
from mdc.MDCButton import MDCButton
from mdc.MDCFormField import MDCFormField, MDCCheckbox, MDCForm
from mdc.MDCLinearProgress import MDCLinearProgress


from browser import document, html

########################################################################

class Widgets:

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        self.widgets = {}

    # ----------------------------------------------------------------------
    def fix_value(self, value):
        """"""
        if isinstance(value, int):
            return value
        elif isinstance(value, float) and value.is_integer():
            return int(value)
        elif isinstance(value, float):
            return round(value, 2)
        elif isinstance(value, str):
            return value

    # ----------------------------------------------------------------------
    def get_value(self, id):
        """"""
        v = self.widgets.get(id)
        if isinstance(v, (list, tuple)):
            return list(map(self.fix_value, v))
        else:
            return self.fix_value(v)

    # ----------------------------------------------------------------------
    def label(self, text, typo='body1', style={}, *args, **kwargs):
        """"""
        label = MDCComponent(html.SPAN(f'{text}'), style=style, *args, **kwargs)
        label.mdc.typography(typo)
        return label

    # ----------------------------------------------------------------------
    def slider(self, label, min, max, value, step=1, unit='', marks=False, on_change=None, id=None, *args, **kwargs):
        """"""
        form = MDCForm()
        label_ = MDCComponent(html.SPAN(f'{label}'))
        label_ .mdc.typography('subtitle1')
        form <= label_
        form <= MDCComponent(html.SPAN(f' {float(value):.1f} {unit}', id=f'value_{id}')).mdc.typography('caption')
        slider_ = form.mdc.Slider('Slider', min=min, max=max, value=value, step=step, marks=marks, *args, **kwargs)

        if on_change:
            slider_.mdc.listen('MDCSlider:change', lambda evt: on_change(self.widgets[id]))

        if id:
            self.widgets[id] = self.fix_value(value)

            def set_value(id, value):
                self.widgets[id] = float(value)
                document.select_one(f'#value_{id}').html = f' {self.get_value(id)} {unit}'

            slider_.mdc.listen('MDCSlider:input', lambda event: set_value(id, slider_.mdc.getValue()))

        return form

    # ----------------------------------------------------------------------
    def range_slider(self, label, min, max, value_lower, value_upper, step, unit='', on_change=None, id=None, *args, **kwargs):
        """"""
        form = MDCForm()
        label_ = MDCComponent(html.SPAN(f'{label}'))
        label_ .mdc.typography('subtitle1')
        form <= label_
        form <= MDCComponent(html.SPAN(f' {float(value_lower):.1f}-{float(value_upper):.1f} {unit}', id=f'value_{id}')).mdc.typography('caption')
        slider_ = form.mdc.RangeSlider('Slider', min, max, value_lower, value_upper, step, *args, **kwargs)

        if on_change:
            slider_.mdc.listen('MDCSlider:change', lambda evt: on_change(self.widgets[id]))

        if id:
            self.widgets[id] = [self.fix_value(value_lower), self.fix_value(value_upper)]

            def set_value(id, value):
                self.widgets[id] = [float(value[0]), float(value[1])]
                document.select_one(f'#value_{id}').html = f' {self.get_value(id)[0]}-{self.get_value(id)[1]} {unit}'

            slider_.mdc.listen('MDCSlider:input', lambda event: set_value(id, [slider_.mdc.getValueStart(), slider_.mdc.getValue()]))

        return form

    # ----------------------------------------------------------------------
    def radios(self, label, radios, on_change=None, id=None):
        """"""
        label = MDCComponent(html.SPAN(f'{label}'))
        label.mdc.typography('subtitle1')
        radios_ = []
        form = MDCForm(formfield_style={'width': '100px'})
        form <= label

        for i, (radio, value) in enumerate(radios):
            radios_.append([form.mdc.Radio(radio, name=id, checked=(i == 0)), value])

        if id:
            self.widgets[id] = radios[0][1]

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
    def checkbox(self, label, checkboxes, on_change=None, id=None):
        """"""
        label = MDCComponent(html.SPAN(f'{label}'))
        label.mdc.typography('subtitle1')
        checkbox_ = []
        form = MDCForm(formfield_style={'width': '100px'})
        form <= label

        for checkbox, checked in checkboxes:
            checkbox_.append([form.mdc.Checkbox(checkbox, name=id, checked=checked), checkbox])

        if id:
            self.widgets[id] = [ch[0] for ch in checkboxes if ch[1]]

            def set_value():
                def wrap(evt):
                    self.widgets[id] = [value for ch, value in checkbox_ if ch.mdc.checked]
                return wrap

            for checkbox, _ in checkbox_:
                checkbox.bind('change', set_value())

        if on_change:
            for checkbox, _ in checkbox_:
                checkbox.bind('change', lambda evt: on_change())

        return form

    # ----------------------------------------------------------------------
    def select(self, label, options, value=None, on_change=None, id=None):
        """"""
        label_ = MDCComponent(html.SPAN(f'{label}'))
        label_ .mdc.typography('subtitle1')
        form = MDCForm(formfield_style={'width': '100px', 'min-height': '90px', 'margin-left': '15px'})
        form <= label_
        select_ = form.mdc.Select('', options=options, selected=value)

        if id:
            self.widgets[id] = value

            def set_value():
                def wrap(evt):
                    self.widgets[id] = select_.mdc['value']
                return wrap

            select_.mdc.listen('MDCSelect:change', set_value())

        if on_change:
            select_.mdc.listen('MDCSelect:change', lambda evt: on_change(select_.mdc['value']))

        return form

    # ----------------------------------------------------------------------
    def button(self, label, unelevated=True, on_click=None, style={}, *args, **kwargs):
        """"""
        btn = MDCButton(label, unelevated=unelevated, style=style, *args, **kwargs)
        if on_click:
            btn.bind('click', lambda evt: on_click())
        return btn

    # ----------------------------------------------------------------------
    def switch(self, label, checked=False, on_change=None, id=None):
        """"""
        form = MDCForm(formfield_style={'width': '100%', 'height': '40px'})
        switch_ = form.mdc.Switch(label, checked)
        form.select_one('label').style = {'margin-left': '10px'}

        if on_change:
            switch_.bind('change', lambda *args, **kwargs: on_change(switch_.mdc.checked))

        if id:
            self.widgets[id] = checked

            def set_value():
                def wrap(evt):
                    self.widgets[id] = switch_.mdc.checked
                return wrap

            switch_.bind('change', set_value())

        return form

