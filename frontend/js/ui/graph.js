/* ui/graph.js */
import cytoscape from "../cytoscape.esm.min.mjs";

let cy = null;

export function initializeGraph(graphData, container) {
    container.innerHTML = "";

    cy = cytoscape({
        
        container: container,

        elements: [
            {
                data: {id: 'a'}
            },
            {
                data: {id: 'b'}
            },
            {
                data: {id: 'c'}
            }
        ],

        style: [
            {
                selector: 'node',
                style: {
                    'background-color': '#ffd1d1', 
                    'label': 'data(id)'
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 3,
                    'line-color': '#ebc06a',
                    'target-arrow-color': '#ebc06a',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier'
                }
            }
        ],

        layout: {
            name: 'grid',
            rows: 1
        }
    });
}


export function getGraph() {
    return cy;
}
