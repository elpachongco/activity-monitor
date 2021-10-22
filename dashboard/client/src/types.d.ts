export interface RawActivity {
    actStart: string[], 
    actEnd: string[], 
    inactDuration: number[], 
    processName: string[], 
    windowName: string[],
};

export interface Activity extends RawActivity {

    // [key: string]: number[],
    actDuration: number[],
}

declare global {
    namespace JSX {
        interface IntrinsicElements {
            'div': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
            'canvas': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
            'p': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
            'h1': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
            'h2': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
            'li': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
            'svg': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
            'g': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
            'rect': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
            'text': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
        }
    }
    const React = any;
    const ReactDOM = any;
    const JSX = any;
    const Chart = any;
}

export interface Props {
    [key: string]: any;
};

export class Component {
    [key: string]: any;
}

export interface ChartData { labels: null | string[], data: null | number[] }    


export interface GraphData { 
	labels: any[]; 
	datasets: { 
		label: string; 
		backgroundColor?: string | string[]; 
		borderColor?: string | null; 
		data: number[]; 
		tension?: number; 
		barPercentage?: number; 
		categoryPercentage?: number; 
	}[]
};