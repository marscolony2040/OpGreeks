import React from 'react';
import Plot from 'react-plotly.js';

import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';
import 'react-tabs/style/react-tabs.css';

import go from './imgs/go.png'
import title from './imgs/tx.png'

import Progress_bar from './Progress_bar.js'

export default class App extends React.Component {
  
  constructor(){
    super();

    this.state = {colorx: 'limegreen', nx: 0, response: null, N: 0, tickers: {}, sock: null, response_title: 'Refresh'}
    this.vol_plots = this.vol_plots.bind(this)
    this.delta_plots = this.delta_plots.bind(this)
    this.gamma_plots = this.gamma_plots.bind(this)
    this.theta_plots = this.theta_plots.bind(this)
    this.vega_plots = this.vega_plots.bind(this)
    this.rho_plots = this.rho_plots.bind(this)

    this.handle_change = this.handle_change.bind(this)
    this.handle_submit = this.handle_submit.bind(this)
    this.build_ticks = this.build_ticks.bind(this)
    this.change_tick = this.change_tick.bind(this)
  }
  
  componentDidMount(){
    
    const socket = new WebSocket('ws://localhost:8080')
    socket.onmessage = (evt) => {
      const data = JSON.parse(evt.data)
      if(data.hasOwnProperty("title")){
        this.setState({ response_title: data['title'], colorx: data['color'], color2: data['color2'], nx: data['NX'] })
      } else {
        this.setState({ response: data, response_title: 'Refresh' })
      }
    }
    this.setState({ sock: socket })
  }

  handle_change(evt){
    this.setState({ [evt.target.name] : parseInt(evt.target.value) })
  }

  change_tick(evt){
    const { tickers } = this.state
    tickers[evt.target.name] = evt.target.value
    this.setState({ tickers: tickers })
  }

  handle_submit(evt){
    const { N, tickers, sock } = this.state
    var tick = {}
    for(var i = 0; i < N; i++){
      const namex = "S" + i.toString()
      tick[namex] = tickers[namex]
    }
    sock.send(JSON.stringify(tick))
    evt.preventDefault()
  }

  build_ticks(bg, fg, fg2){
    const { N } = this.state
    const hold = []
    for(var i = 0; i < N; i++){
      const namex = "S" + i.toString()
      hold.push(
        <input name={namex} type="text" onChange={this.change_tick} style={{backgroundColor: fg, color: 'black', width: 100, fontSize: 23, textAlign: "center"}}/>
      )
    }
    return hold
  }

  vol_plots(bg, fg){
    const hold = []
    const { response } = this.state 
    if(response != null){
      response['tickers'].forEach((ix) => {
        hold.push(
          <Plot 
            data={[{
              x: response['x']['call'][ix],
              y: response['y']['call'][ix],
              z: response['vol']['call'][ix],
              type: 'scatter3d',
              mode: 'markers',
              marker: {
                size: 2,
                color: 'limegreen'
              },
              name: 'Call Options'
            },
            {
              x: response['x']['put'][ix],
              y: response['y']['put'][ix],
              z: response['vol']['put'][ix],
              type: 'scatter3d',
              mode: 'markers',
              marker: {
                size: 2,
                color: 'red'
              },
              name: 'Put Options'
            }]}
            layout={{
              title: {
                text: 'Implied Volatility for ' + ix,
                font: {
                  color: fg
                }
              },
              showlegend: false,
              paper_bgcolor: bg,
              plot_bgcolor: bg,
              scene: {
                xaxis: {
                  title: 'Strike Price',
                  color: fg,
                  showgrid: false,
                  autorange: 'reversed'
                },
                yaxis: {
                  title: 'Expiration',
                  color: fg,
                  showgrid: false,
                  autorange: 'reversed'
                },
                zaxis: {
                  title: 'Implied Volatility',
                  color: fg,
                  showgrid: false
                }
              }
            }}
          />
        )

      })
    }
    return hold
  }

  delta_plots(bg, fg){
    const hold = []
    const { response } = this.state 
    if(response != null){
      response['tickers'].forEach((ix) => {
        hold.push(
          <Plot 
            data={[{
              x: response['x']['call'][ix],
              y: response['y']['call'][ix],
              z: response['delta']['call'][ix],
              type: 'scatter3d',
              mode: 'markers',
              marker: {
                size: 2,
                color: 'limegreen'
              },
              name: 'Call Options'
            },
            {
              x: response['x']['put'][ix],
              y: response['y']['put'][ix],
              z: response['delta']['put'][ix],
              type: 'scatter3d',
              mode: 'markers',
              marker: {
                size: 2,
                color: 'red'
              },
              name: 'Put Options'
            }]}
            layout={{
              title: {
                text: 'Delta for ' + ix,
                font: {
                  color: fg
                }
              },
              showlegend: false,
              paper_bgcolor: bg,
              plot_bgcolor: bg,
              scene: {
                xaxis: {
                  title: 'Strike Price',
                  color: fg,
                  showgrid: false,
                  autorange: 'reversed'
                },
                yaxis: {
                  title: 'Expiration',
                  color: fg,
                  showgrid: false,
                  autorange: 'reversed'
                },
                zaxis: {
                  title: 'Delta',
                  color: fg,
                  showgrid: false
                }
              }
            }}
          />
        )

      })
    }
    return hold
  }
  
  gamma_plots(bg, fg){
    const hold = []
    const { response } = this.state 
    if(response != null){
      response['tickers'].forEach((ix) => {
        hold.push(
          <Plot 
            data={[{
              x: response['x']['call'][ix],
              y: response['y']['call'][ix],
              z: response['gamma']['call'][ix],
              type: 'scatter3d',
              mode: 'markers',
              marker: {
                size: 2,
                color: 'limegreen'
              },
              name: 'Gamma Plots'
            }]}
            layout={{
              title: {
                text: 'Gamma for ' + ix,
                font: {
                  color: fg
                }
              },
              showlegend: false,
              paper_bgcolor: bg,
              plot_bgcolor: bg,
              scene:{
                xaxis: {
                  title: 'Strike Price',
                  color: fg,
                  showgrid: false,
                  autorange: 'reversed'
                },
                yaxis: {
                  title: 'Expiration',
                  color: fg,
                  showgrid: false,
                  autorange: 'reversed'
                },
                zaxis: {
                  title: 'Gamma',
                  color: fg,
                  showgrid: false
                }
              }
            }}
          />
        )

      })
    }
    return hold
  }
  
  theta_plots(bg, fg){
    const hold = []
    const { response } = this.state 
    if(response != null){
      response['tickers'].forEach((ix) => {
        hold.push(
          <Plot 
            data={[{
              x: response['x']['call'][ix],
              y: response['y']['call'][ix],
              z: response['theta']['call'][ix],
              type: 'scatter3d',
              mode: 'markers',
              marker: {
                size: 2,
                color: 'limegreen'
              },
              name: 'Call Options'
            },
            {
              x: response['x']['put'][ix],
              y: response['y']['put'][ix],
              z: response['theta']['put'][ix],
              type: 'scatter3d',
              mode: 'markers',
              marker: {
                size: 2,
                color: 'red'
              },
              name: 'Put Options'
            }]}
            layout={{
              title: {
                text: 'Theta for ' + ix,
                font: {
                  color: fg
                }
              },
              showlegend: false,
              paper_bgcolor: bg,
              plot_bgcolor: bg,
              scene: {
                xaxis: {
                  title: 'Strike Price',
                  color: fg,
                  showgrid: false,
                  autorange: 'reversed'
                },
                yaxis: {
                  title: 'Expiration',
                  color: fg,
                  showgrid: false,
                  autorange: 'reversed'
                },
                zaxis: {
                  title: 'Theta',
                  color: fg,
                  showgrid: false
                }
              }
            }}
          />
        )

      })
    }
    return hold
  }

  vega_plots(bg, fg){
    const hold = []
    const { response } = this.state 
    if(response != null){
      response['tickers'].forEach((ix) => {
        hold.push(
          <Plot 
            data={[{
              x: response['x']['call'][ix],
              y: response['y']['call'][ix],
              z: response['vega']['call'][ix],
              type: 'scatter3d',
              mode: 'markers',
              marker: {
                size: 2,
                color: 'limegreen'
              },
              name: 'Vega Plots'
            }]}
            layout={{
              title: {
                text: 'Vega for ' + ix,
                font: {
                  color: fg
                }
              },
              showlegend: false,
              paper_bgcolor: bg,
              plot_bgcolor: fg,
              scene: {
                xaxis: {
                  title: 'Strike Price',
                  color: fg,
                  showgrid: false,
                  autorange: 'reversed'
                },
                yaxis: {
                  title: 'Expiration',
                  color: fg,
                  showgrid: false,
                  autorange: 'reversed'
                },
                zaxis: {
                  title: 'Vega',
                  color: fg,
                  showgrid: false
                }
              }
            }}
          />
        )

      })
    }
    return hold
  }

  rho_plots(bg, fg){
    const hold = []
    const { response } = this.state 
    if(response != null){
      response['tickers'].forEach((ix) => {
        hold.push(
          <Plot 
            data={[{
              x: response['x']['call'][ix],
              y: response['y']['call'][ix],
              z: response['rho']['call'][ix],
              type: 'scatter3d',
              mode: 'markers',
              marker: {
                size: 2,
                color: 'limegreen'
              },
              name: 'Call Options'
            },
            {
              x: response['x']['put'][ix],
              y: response['y']['put'][ix],
              z: response['rho']['put'][ix],
              type: 'scatter3d',
              mode: 'markers',
              marker: {
                size: 2,
                color: 'red'
              },
              name: 'Put Options'
            }]}
            layout={{
              title: {
                text: 'Rho for ' + ix,
                font: {
                  color: fg
                }
              },
              showlegend: false,
              paper_bgcolor: bg,
              plot_bgcolor: fg,
              scene:{
                xaxis: {
                  title: 'Strike Price',
                  color: fg,
                  showgrid: false,
                  autorange: 'reversed'
                },
                yaxis: {
                  title: 'Expiration',
                  color: fg,
                  showgrid: false,
                  autorange: 'reversed'
                },
                zaxis: {
                  title: 'Rho',
                  color: fg,
                  showgrid: false
                }
              }
            }}
          />
        )

      })
    }
    return hold
  }

  render() {

    const bg = 'black'
    const fg = 'cyan'
    const fg2 = 'yellow'


    return (
      <React.Fragment>
        <center>
          <img src={title} style={{width: 1000, height: 100}} onClick={this.handle_submit}/>
          <div style={{backgroundColor: bg, color: fg, fontSize: 25}}>Number of Stocks</div>
          <br/>
          <div><input name="N" type="number" step="1" min="0" value={this.state.N} onChange={this.handle_change} style={{backgroundColor: fg, color: 'black', width: 100, fontSize: 23, textAlign: "center"}}/></div>
          <br/>
          <div>{this.build_ticks(bg, fg, fg2)}</div>
          <br/>
          
        </center>
        <center>
          <br/>
          <tr>
            <td style={{backgroundColor: bg, color: 'limegreen', fontSize: 23}}>Call Options</td>&nbsp;&nbsp;
            <td style={{backgroundColor: bg, color: 'red', fontSize: 23}}>Put Options</td>
          </tr>
          <br/>
          <div style={{color: fg2, fontSize: 19}}>
            {this.state.response_title}
          </div>
          <div>
            <Progress_bar bgcolor={this.state.colorx} progress={this.state.nx} height={30} fgcolor={this.state.color2}/>
          </div>
          <br/>
        </center>
        <center>
          <Tabs style={{backgroundColor: bg, color: fg, fontSize: 25}}>
            <TabList>
              <Tab>Implied Volatility</Tab>
              <Tab>Delta</Tab>
              <Tab>Gamma</Tab>
              <Tab>Theta</Tab>
              <Tab>Vega</Tab>
              <Tab>Rho</Tab>
            </TabList>

            <TabPanel>
              {this.vol_plots(bg, fg)}
            </TabPanel>
            <TabPanel>
              {this.delta_plots(bg, fg)}
            </TabPanel>
            <TabPanel>
              {this.gamma_plots(bg, fg)}
            </TabPanel>
            <TabPanel>
              {this.theta_plots(bg, fg)}
            </TabPanel>
            <TabPanel>
              {this.vega_plots(bg, fg)}
            </TabPanel>
            <TabPanel>
              {this.rho_plots(bg, fg)}
            </TabPanel>
          </Tabs>
          </center>
      </React.Fragment>
    );
  }
}