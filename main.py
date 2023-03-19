from bokeh.plotting import figure, curdoc
from bokeh.models.sources import ColumnDataSource
from bokeh.models import Button, TextInput, Slider, Toggle, TextAreaInput
from bokeh.layouts import column, row, layout

from scipy.optimize import curve_fit

from SQLClient import SQLClient

from Device import Device
from DigitalTwin import DigitalTwin

run_time = 0

# define data structure
data = {'time': [0], 'biomass': [0], 'do': [0], 'glucose': [6.83], 'lac': [0],
        'agitation': [60]}
source_dt = ColumnDataSource(data)

data = {'time': [0], 'biomass': [0]}
source_NIR = ColumnDataSource(data)

data = {'time': [0], 'glucose': [6.83]}
source_glu = ColumnDataSource(data)

data = {'time': [0], 'lac': [0]}
source_lac = ColumnDataSource(data)

database = SQLClient()

# create a plot and style its properties

p = figure(y_axis_label='Cell Density', tools='pan,wheel_zoom,box_zoom,reset',
           sizing_mode="stretch_both", height=180)

p.line('time', 'biomass', source=source_dt, color='blue', line_width=2, legend_label='cell')
p.circle('time', 'biomass', source=source_NIR, color='red', legend_label='cell detector')

p2 = figure(y_axis_label='Concentration', tools='pan,wheel_zoom,box_zoom,reset',
            sizing_mode="stretch_both", height=180)
p2.line('time', 'glucose', source=source_dt, color='blue', line_width=2, legend_label='glucose')
p2.circle('time', 'glucose', source=source_glu, color='red', legend_label='glucose sample')

p2.line('time', 'lac', source=source_dt, color='yellow', line_width=2, legend_label='lactic acid')
p2.circle('time', 'lac', source=source_lac, color='cyan', legend_label='lactic acid sample')

p3 = figure(y_axis_label='Dissolved Oxygen', tools='pan,wheel_zoom,box_zoom,reset',
            sizing_mode="stretch_both", height=180)
p3.line('time', 'do', source=source_dt, color='blue', line_width=2, legend_label='dissoved oxygen')

p4 = figure(x_axis_label='Time, t (s)', y_axis_label='Rocking rate (rpm)', tools='pan,wheel_zoom,box_zoom,reset',
            sizing_mode="stretch_both", height=180)
p4.line('time', 'agitation', source=source_dt, color='blue', line_width=2, legend_label='rocking rate')

btn_width = 150
text_width = 150

start_btn = Toggle(label='start', button_type='danger', width=btn_width)
device_btn = Toggle(label='connect device', button_type='success', width=btn_width)
reset_btn = Button(label='reset', button_type='danger', css_classes=['albtn'])

inoculate_btn = Button(label='inoculate', button_type='warning', css_classes=['albtn'], width=btn_width)
inoculate_text = TextInput(title='cell inoculated', width=text_width)

predict_btn = Button(label='predict', button_type='success', css_classes=['albtn'], width=btn_width)
predict_text = TextInput(title='glucose concentration to change media', width=text_width)

maintain_text = TextInput(title='glucose concentration to maintain', width=text_width, disabled=True)
maintain_btn = Toggle(label='auto', button_type='success', css_classes=['albtn'], width=btn_width, disabled=True)

feed_btn = Button(label='media change', button_type='warning', width=btn_width)

sampling_btn = Button(label='cell count', button_type='primary', width=btn_width)

shake_slider = Slider(start=40, end=90, value=60, step=10, title='rocking rate (rpm)', width=btn_width)
shake_btn = Button(label='set rocking rate', button_type='primary', width=btn_width)

angle_slider = Slider(start=7, end=15, value=7, step=1, title='rocking angle (°)', width=btn_width)
angle_btn = Button(label='set rocking angle', button_type='primary', width=btn_width)

glucose_btn = Button(label='glucose sampling', button_type='warning', css_classes=['albtn'], width=btn_width)
glucose_text = TextInput(title='glucose (g/L)', width=text_width)

lac_btn = Button(label='lac sampling', button_type='warning', css_classes=['albtn'], width=btn_width)
lac_text = TextInput(title='lactic acid (g/L)', width=text_width)

reminder = TextAreaInput(title='the Digital Twin\'s status is shown here.', value='None', height=200, width=300,
                         disabled=True)

dt = DigitalTwin()

device = Device()


def sampling_callback():
    density = device.sampling()
    dt.data.biomass = density
    new_data = {'time': [run_time], 'biomass': [density]}
    source_NIR.stream(new_data)


def shake_callback():
    # device.change_shake(shake_slider.value)
    dt.data.agit = int(shake_slider.value)


def predict_callback():
    dtt = DigitalTwin()
    dtt.data.glucose = dt.data.glucose
    dtt.data.biomass = dt.data.biomass
    tt = 0
    while dtt.data.glucose > float(predict_text.value):
        dtt.update()
        tt += 1
    reminder.value = "After {} h, Glucose reaches {} g/L, cell count reaches {} cell/mL".format(tt / 3600,
                                                                                                dtt.data.glucose,
                                                                                                dtt.data.biomass)


def device_callback():
    if not device_btn.active:
        device.connect()
    else:
        device.disconnect()


def glucose_callback():
    global run_time
    glucose = 0
    try:
        glucose = float(glucose_text.value)
    except ValueError:
        return
    database.insert_glucose(run_time, glucose)
    # print(source_glu.data['glucose'][-1])

    def f(t, q):
        res = []
        for tt in t:
            dtt = DigitalTwin()
            dtt.data.biomass = source_dt.data['biomass'][int(t[0])]
            dtt.data.glucose = source_glu.data['glucose'][-1]
            for second in range(int(t[0]), int(tt)):
                dtt.data.biomass = source_dt.data['biomass'][second]
                dtt.update()
            res.append(dtt.data.glucose)
        return res

    para, _ = curve_fit(f, [source_glu.data['time'][-1], run_time], [source_glu.data['glucose'][-1], glucose],
                        p0=-1e-12, maxfev=100000)
    dt.reaction.set_qglu(para[0])

    new_data = {'time': [run_time], 'glucose': [glucose]}
    source_glu.stream(new_data)
    dt.data.glucose = glucose
    reminder.value = "Glucose is updated to {} g/L".format(glucose)


def lac_callback():
    global run_time
    lac = 0
    try:
        lac = float(lac_text.value)
    except ValueError:
        return
    database.insert_lac(run_time, lac)
    def f(t, q):
        res = []
        for tt in t:
            dtt = DigitalTwin()
            dtt.data.biomass = source_dt.data['biomass'][int(t[0])]
            dtt.data.glucose = source_glu.data['glucose'][-1]
            dtt.data.lac = source_lac.data['lac'][-1]
            for second in range(int(t[0]), int(tt)):
                dtt.data.biomass = source_dt.data['biomass'][second]
                dtt.update()
            res.append(dtt.data.lac)
        return res

    para, _ = curve_fit(f, [source_lac.data['time'][-1], run_time], [source_lac.data['lac'][-1], lac],
                        p0=-1e-12, maxfev=100000)
    dt.reaction.set_qlac(para[0])

    new_data = {'time': [run_time], 'lac': [lac]}
    source_lac.stream(new_data)
    dt.data.lac = lac
    reminder.value = "Lactic acid is updated to {} g/L".format(lac)

def angle_callback():
    # device.change_angle(angle_slider.value)
    pass

def feed_callback():
    global run_time
    dt.data.glucose = 6.83
    dt.data.lac = 0
    reminder.value = "media changed"

        
def inoculate_callback():
    dt.data.biomass += float(inoculate_text.value)
        

lac_btn.on_click(lac_callback)

sampling_btn.on_click(sampling_callback)
shake_btn.on_click(shake_callback)
angle_btn.on_click(angle_callback)
glucose_btn.on_click(glucose_callback)
predict_btn.on_click(predict_callback)
feed_btn.on_click(feed_callback)
device_btn.on_click(device_callback)
inoculate_btn.on_click(inoculate_callback)


def update_plot():
    if start_btn.active:
        global run_time
        run_time += 1
        dt.update()
        new_data = {'time': [run_time], 'biomass': [dt.data.biomass], 'glucose': [dt.data.glucose], 'do': [dt.data.DO],
                    'lac': [dt.data.lac], 'agitation': [dt.data.agit]}

        database.insert_dt(run_time, dt.data.biomass, dt.data.DO, dt.data.glucose, dt.data.lac, dt.data.agit)

        source_dt.stream(new_data)
        sync_data = ''

        if device.is_connected() and run_time % 900 == 0:
            device.sampling()

        if device.is_connected():
            sync_data = device.get_data()

            if sync_data[0] == 'CE':
                new_biomass = int(sync_data[2:])
                database.insert_NIR(run_time, new_biomass)

                def f(t, q):
                    res = []
                    for tt in t:
                        dtt = DigitalTwin()
                        dtt.data.biomass = source_dt.data['biomass'][int(t[0])]
                        for second in range(int(t[0]), int(tt)):
                            dtt.update()
                        res.append(dtt.data.biomass)
                    return res

                para, _ = curve_fit(f, [source_NIR.data['time'][-1], run_time],
                                    [source_NIR.data['biomass'][-1], new_biomass], p0=1e-5,
                                    maxfev=100000)
                dt.set_umax = para[0]

                new_data = {'time': [run_time], 'biomass': [new_biomass]}
                source_NIR.stream(new_data)


UI = row([column(children=[row(glucose_text, glucose_btn), row(lac_text, lac_btn), row(sampling_btn, feed_btn),
                           row(inoculate_text, inoculate_btn), row(shake_slider, shake_btn),
                           row(angle_slider, angle_btn), row(predict_text, predict_btn),
                           row(maintain_text, maintain_btn), reminder, row(device_btn, start_btn)]),
          column(children=[p, p2, p3, p4], sizing_mode='stretch_width')])

curdoc().add_root(UI)

idx = curdoc().add_periodic_callback(update_plot, 1000)
