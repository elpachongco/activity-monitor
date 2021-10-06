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