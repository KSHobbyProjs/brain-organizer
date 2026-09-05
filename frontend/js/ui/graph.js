/* ui/graph.js */
import cytoscape from "../cytoscape.esm.min.mjs";

/* colors for graphing nodes and edges */
const root = getComputedStyle(document.documentElement);
const nodeColor = root.getPropertyValue("--accent-color");
const edgeColor = root.getPropertyValue("--text-primary");


let cy = null;

export function initializeGraph(graphData, container) {
    container.innerHTML = "";
    cy = cytoscape({
     
        container: container,

        elements: graphData.elements,

        style: [
            {
                selector: 'node',
                style: {
                    'background-color': nodeColor, 
                    'border-color': edgeColor,
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 3,
                    'line-color': edgeColor,
                    'curve-style': 'bezier'
                }
            }
        ],

        layout: {
            name: 'preset',
        }
   
    });
}


export function getGraph() {
    return cy;
}
