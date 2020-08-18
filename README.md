# TSVPS

[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

Python script to solve a NP-hard problem in combinatorial optimization similar to the [Traveling-Salesman Problem](https://en.wikipedia.org/wiki/Travelling_salesman_problem) for a specific dataset that can be connected to the [MapBox API](https://www.mapbox.com/). This algorithm uses the Miller–Tucker–Zemlin formulation approach.

<p align="center">
  <img width="460" src="https://thumbs.gfycat.com/HalfSpitefulAzurevase-max-1mb.gif">
</p>

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You will need Gurobi Optimization library, you can try it out with a free trial here.

```
https://www.gurobi.com/free-trial/
```

### Running

The published script comes ready to run with automatic generation of its dataset. 

```
py main.py
```

### Configuration

Further configuration can be achieved by adding a MapBox API Key and enabling XRouter in the router module.

## Built With

* [Gurobi](https://www.gurobi.com/free-trial/) - Python optimization library
* [MapBox](https://www.mapbox.com/) - Map & Location API

## Authors

* **@nbcl** - *Python Algorithm & Mathematical Optimization Model* 

* **Matías Fuentealba** - *Mathematical Optimization Model*  

* **Sebastián Benitez** - *Mathematical Optimization Model*  

* **Mauricio Alvarez** - *Mathematical Optimization Model*  

* **Felipe Machuca** - *Mathematical Optimization Model*  


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
