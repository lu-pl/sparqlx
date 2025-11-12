# Changelog

## [0.4.0](https://github.com/lu-pl/sparqlx/compare/v0.3.0...v0.4.0) (2025-11-12)


### Features

* add event-based logging ([04fe325](https://github.com/lu-pl/sparqlx/commit/04fe3256176f7d319ba1bfce7b1edc72d5af98c8))
* check for missing headers.content-type in _convert_graph ([3e845db](https://github.com/lu-pl/sparqlx/commit/3e845db5cd0918c2387b555a507aa20fc68a4e34))
* introduce _TRequestDataValue for httpx data mappings ([11ea18f](https://github.com/lu-pl/sparqlx/commit/11ea18f79d7c9e816870af8e59c9892dd1866923))
* set header content-type to "application/x-www-form-urlencoded" ([b446944](https://github.com/lu-pl/sparqlx/commit/b44694426d6b6248019808195b76284bf163e610))
* **types:** introduce Query types for enhanced static return types ([2cf6710](https://github.com/lu-pl/sparqlx/commit/2cf67104e34c022c50fa1d9e6813f5587ff2c611))


### Bug Fixes

* Use application/rdf+xml as Graph response type for XML ([6453dd3](https://github.com/lu-pl/sparqlx/commit/6453dd35be2c47f93652972a1057f0d2303163ab))


### Documentation

* add recipes section and streaming recipes to readme ([4658ad7](https://github.com/lu-pl/sparqlx/commit/4658ad793c6283c342e2207a8dd677d8ffb953d0))
* add section on converted result type narrowing to the README ([17bc5b5](https://github.com/lu-pl/sparqlx/commit/17bc5b5134c3b1fd58f824e866b9d10032dcc189))
* align `sparqlx` references in docs ([0cecb08](https://github.com/lu-pl/sparqlx/commit/0cecb08a38530b83e1a04c6535963a9b09db4038))
* correct minor typo in JSON streaming recipe ([98fd0c2](https://github.com/lu-pl/sparqlx/commit/98fd0c23d236db234a142181dc040bec0fc9aaa0))
* minor doc cleanup ([c7434cf](https://github.com/lu-pl/sparqlx/commit/c7434cffa6b687297e0cc37c87d63074820b7906))

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
