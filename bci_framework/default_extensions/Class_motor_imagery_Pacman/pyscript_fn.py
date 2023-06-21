

# ----------------------------------------------------------------------
def render_plotly_fig__(fig, chart):
    import json
    import plotly
    import js
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    js.Plotly.newPlot(chart, js.JSON.parse(graphJSON), {})

# # ----------------------------------------------------------------------
# @pyscript()
# def brython_serializer(data):
    # """"""
    # return json.dumps(data)
