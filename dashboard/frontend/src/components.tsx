import { React, Props, Chart} from "./types";

function HeatmapSquare(props: Props) {
	return (<div className="heatmap_square" value={props.value} />);
}


class Heatmap extends React.Component {
    props: any;
	render() {
		let squares = [];
		for (let i=0; i < this.props.squares; i++)	
			squares.push(<HeatmapSquare value={i} />);

		return (<div className="heatmap">{squares}</div>);
	}
}


class Linegraph extends React.Component {
    props: any;
    canvasRef: any;
	constructor(props: Props) 
	{
		super(props);
		this.canvasRef = React.createRef();
	}

	createGraph() {
		const labels = [
		  'January',
		  'February',
		  'March',
		  'April',
		  'May',
		  'June',
		];
		
		const data = {
		labels: labels,
		datasets: [{
			label: 'My First dataset',
			backgroundColor: 'rgb(255, 99, 132)',
			borderColor: 'rgb(255, 99, 132)',
			data: [0, 10, 5, 2, 20, 30, 45],
		}]
		};
	
		const graphConfig = {
			type: 'line',
			data: data,
			options: {}
		};
		new Chart(this.canvasRef.current, graphConfig);
	}

	componentDidMount() {
		this.createGraph();
	}

	render() {
		return (
			<div className="lineGraph">
				<canvas id="graphCanvas" ref={this.canvasRef} width={this.props.width} 
				height={this.props.height} />
			</div>
		)
	}
}

export class Dashboard extends React.Component {
    props: any;
	componentDidMount() {
	}

	render() {
		return (
			<div className="dashboard">
				<Heatmap squares={25}/>
				<Linegraph width={20} height={20}/>
			</div>
		);
	}
}