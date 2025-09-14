# Changelog

## [0.3.0](https://github.com/lu-pl/sparqlx/compare/v0.2.0...v0.3.0) (2025-09-14)


### ⚠ BREAKING CHANGES

* change SELECT conversion type to list[_SPARQLBinding]

### Features

* change SELECT conversion type to list[_SPARQLBinding] ([4789f1a](https://github.com/lu-pl/sparqlx/commit/4789f1a83636473fff2bac66840c6d93b4ee3cd7))

## [0.2.0](https://github.com/lu-pl/sparqlx/compare/v0.1.0...v0.2.0) (2025-09-12)


### ⚠ BREAKING CHANGES

* implement SPARQL Update operations

### Features

* implement SPARQL Update operations ([2c1f3b8](https://github.com/lu-pl/sparqlx/commit/2c1f3b871065a047e1c832b8f9eec905d42c1267))
* implement support for graph uri and version parameters ([9c4ff00](https://github.com/lu-pl/sparqlx/commit/9c4ff00dc57c745fb95e9d65e8e20d18ead37e94))
* return current instance from context manager entry ([55fe5ba](https://github.com/lu-pl/sparqlx/commit/55fe5ba3acf555d96319c274ae293fc0296caa9f))


### Bug Fixes

* add bool to convert union type ([3ed4618](https://github.com/lu-pl/sparqlx/commit/3ed46185b834b0eb799f37d64da0a7738ecbf32a))
* drop graph in fuseki_service_graph per function ([3cf33a0](https://github.com/lu-pl/sparqlx/commit/3cf33a08e3234c076ec3cec091068b9dbd06dfca))
* pass only _client/_aclient properties to context SPARQLWrapper ([287eb68](https://github.com/lu-pl/sparqlx/commit/287eb684bc5b6ea6b6da0cb93374500c0eeff66f))
* set oxigraph_service_graph fixture to function scope ([f6c566f](https://github.com/lu-pl/sparqlx/commit/f6c566fef02dffbca08a8e0ed541f5a25900ebe7))

## 0.1.0 (2025-08-28)


### Features

* add _convert_ask function ([46eba25](https://github.com/lu-pl/sparqlx/commit/46eba2592d30ed27bb06b80a0a6b071a4e8367a7))
* expose SPARQLx types for public use ([4d41f1c](https://github.com/lu-pl/sparqlx/commit/4d41f1ced05e1a512de79f680de1fb33f0e839d7))
* extract get_query_type ([65e5e30](https://github.com/lu-pl/sparqlx/commit/65e5e308a01a3f2fef18b5a41cb7ee70cf7f2fb8))
* implement ASK query conversion ([e60ab90](https://github.com/lu-pl/sparqlx/commit/e60ab903d4c6c284349c8cf7fcbf7d18b0f64d89))
* implement SPARQLWrapper functionality ([fd17ede](https://github.com/lu-pl/sparqlx/commit/fd17edec8b113090c975b0aded6f3a0ee5bbe362))
* simplify MimeTypeMaps ([5b920e9](https://github.com/lu-pl/sparqlx/commit/5b920e906b4b538110ac5d95a93fe9e76704b46a))
* **tests:** implement test graph fixture ([6fb08ba](https://github.com/lu-pl/sparqlx/commit/6fb08baa75be165c62356c1a0d3ba00335bc24d5))


### Documentation

* provide basic readme ([632f779](https://github.com/lu-pl/sparqlx/commit/632f7791a5e2d01ebd5f51ddb46cbc8126bdb963))
