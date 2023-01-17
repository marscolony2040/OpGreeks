import React from 'react';
import Plot from 'react-plotly.js';

import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';
import 'react-tabs/style/react-tabs.css';

export default class App extends React.Component {
  
  constructor(){
    super();

    this.state = {response: null}
    this.vol_plots = this.vol_plots.bind(this)
    this.delta_plots = this.delta_plots.bind(this)
    this.gamma_plots = this.gamma_plots.bind(this)
  }
  
  componentDidMount(){
    
    const socket = new WebSocket('ws://localhost:8080')
    socket.onmessage = (evt) => {
      this.setState({ response: JSON.parse(evt.data) })
    }
    
  }

  vol_plots(){
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
                size: 1,
                color: 'blue'
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
                size: 1,
                color: 'red'
              },
              name: 'Put Options'
            }]}
            layout={{
              title: 'Implied Volatility for ' + ix,
              xaxis: {
                title: 'Strike Price'
              },
              yaxis: {
                title: 'Expiration'
              },
              zaxis: {
                title: 'Implied Volatility'
              }
            }}
          />
        )

      })
    }
    return hold
  }

  delta_plots(){
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
                size: 1,
                color: 'blue'
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
                size: 1,
                color: 'red'
              },
              name: 'Put Options'
            }]}
            layout={{
              title: 'Implied Volatility for ' + ix,
              xaxis: {
                title: 'Strike Price'
              },
              yaxis: {
                title: 'Expiration'
              },
              zaxis: {
                title: 'Delta'
              }
            }}
          />
        )

      })
    }
    return hold
  }
  
  gamma_plots(){
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
                size: 1,
                color: 'blue'
              },
              name: 'Gamma Plots'
            }]}
            layout={{
              title: 'Gamma for ' + ix,
              xaxis: {
                title: 'Strike Price'
              },
              yaxis: {
                title: 'Expiration'
              },
              zaxis: {
                title: 'Gamma'
              }
            }}
          />
        )

      })
    }
    return hold
  }
  
  render() {
    return (
      <React.Fragment>
        <center>
          <Tabs>
            <TabList>
              <Tab>Implied Volatility</Tab>
              <Tab>Delta</Tab>
              <Tab>Gamma</Tab>
            </TabList>

            <TabPanel>
              {this.vol_plots()}
            </TabPanel>
            <TabPanel>
              {this.delta_plots()}
            </TabPanel>
            <TabPanel>
              {this.gamma_plots()}
            </TabPanel>
          </Tabs>
          </center>
      </React.Fragment>
    );
  }
}