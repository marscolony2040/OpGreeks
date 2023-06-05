import React from 'react'

const Progress_bar = ({bgcolor,progress,height,fgcolor}) => {
	
	const Parentdiv = {
		height: height,
		width: '1000px',
		backgroundColor: 'whitesmoke',
		borderRadius: 40,
		margin: 50
	}
	
	const Childdiv = {
		height: '100%',
		width: `${progress}%`,
		backgroundColor: bgcolor,
	borderRadius:40,
		textAlign: 'center'
	}
	
	const progresstext = {
		padding: 10,
		color: fgcolor,
		fontWeight: 900
	}
		
	return (
	<div style={Parentdiv}>
	<div style={Childdiv}>
		<span style={progresstext}>{`${progress}%`}</span>
	</div>
	</div>
	)
}

export default Progress_bar;
