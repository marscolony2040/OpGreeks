import React from 'react';
import Plot from 'react-plotly.js';

export default class App extends React.Component {
  
  constructor(){
    super();

    this.state = {response: null}
    this.plots = this.plots.bind(this)
  }
  
  componentDidMount(){
    
    const socket = new WebSocket('ws://localhost:8080')
    socket.onmessage = (evt) => {
      this.setState({ response: JSON.parse(evt.data) })
    }
    
  }

  plots(){
    const hold = []
    const { response } = this.state 
    if(response != null){
      response['tickers'].forEach((ix) => {
        hold.push(
          <Plot 
            data={[{
              x: response['x'][ix],
              y: response['y'][ix],
              z: response['z'][ix],
              type: 'scatter3d',
              mode: 'markers',
              marker: {
                size: 1
              }
            }]}
            layout={{
              title: 'Implied Volatility for ' + ix
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
        {this.plots()}
      </React.Fragment>
    );
  }
}