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
      hold.push(
        <Plot 
          data={[{
            x: response['x']['AAPL'],
            y: response['y']['AAPL'],
            z: response['z']['AAPL'],
            type: 'scatter3d'
          }]}
        />
      )
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