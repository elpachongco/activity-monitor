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


export declare const React = any;
export declare const ReactDOM = any;
export declare const JSX = any;
export declare const Chart = any;

declare global {
    namespace JSX {
        interface IntrinsicElements {
            'div': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
            'canvas': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
        }
    }
}

export interface Props {
    [key: string]: any;
};

export class Component {
    [key: string]: any;
}