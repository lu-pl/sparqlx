# Changelog

## [0.10.0](https://github.com/lu-pl/sparqlx/compare/v0.9.0...v0.10.0) (2026-02-09)


### Features

* add `Server` to HTTP response headers for rdflib.Graph targets ([f8a14f5](https://github.com/lu-pl/sparqlx/commit/f8a14f57686afe359770f5f5ff7c09caba0b3460))
* suppress open client warnings in SPARQLWrapper.queries ([aae15c2](https://github.com/lu-pl/sparqlx/commit/aae15c260af46a52db708a08fea7d74be8aea2c1))


### Documentation

* add docs section on SPARQL result conversion ([0edc822](https://github.com/lu-pl/sparqlx/commit/0edc822b14faf96fd7394818e5cba59ed60d5181))
* introduce docs folder and move SPARQL Protocol docs ([22fafea](https://github.com/lu-pl/sparqlx/commit/22fafea4e4fcf4bf420230beaa6739d6dbee7497))
* move Recipes and Graph target docs to docs folder ([f9997ba](https://github.com/lu-pl/sparqlx/commit/f9997ba23ff776b0ca8f6beef47333f33bfea91d))

## [0.9.0](https://github.com/lu-pl/sparqlx/compare/v0.8.0...v0.9.0) (2026-02-01)


### ⚠ BREAKING CHANGES

* forward from_rdf_source kwargs to parsing

### Features

* add `raise_for_status: bool` flag ([aadf2cc](https://github.com/lu-pl/sparqlx/commit/aadf2cc739d78933c91e4d92e18d88ebd1d35d7f))
* implement a SPARQLWrapper constructor for RDF sources ([948fa94](https://github.com/lu-pl/sparqlx/commit/948fa94398bdc9174efcf8259c750869eef1a740))
* introduce RDFParseSource type ([b395a95](https://github.com/lu-pl/sparqlx/commit/b395a95e705e88179d55b1f931ca5bd4cbc96cb1))


### Bug Fixes

* always raise for status if convert=True ([81ae28e](https://github.com/lu-pl/sparqlx/commit/81ae28eda47431590518a92a68aadcd1fbeb21f6))
* forward from_rdf_source kwargs to parsing ([ecc312b](https://github.com/lu-pl/sparqlx/commit/ecc312b5ae8e4e1d36977be0e997f44f22d6785f))


### Documentation

* add rdflib.Graph target README section ([a70b5b3](https://github.com/lu-pl/sparqlx/commit/a70b5b36fbc85baec352bb47f98841f4adf12acb))
* update from_rdf_source info with kwargs forwarding info ([a264c14](https://github.com/lu-pl/sparqlx/commit/a264c14a82bc96100245bb7d3c09cec0760d282a))

## [0.8.0](https://github.com/lu-pl/sparqlx/compare/v0.7.0...v0.8.0) (2026-01-28)


### ⚠ BREAKING CHANGES

* make SPARQLWrapper configuration attribues private

### Features

* implement httpx.Transport Facades ([ed0a8b9](https://github.com/lu-pl/sparqlx/commit/ed0a8b934a7d1cd4b4c2bde6c0ad5a8b874e758e))
* implement rdflib.Graph targets ([433ed6b](https://github.com/lu-pl/sparqlx/commit/433ed6b43a2a740be497cb2da4de509c522e7a07))
* reject invalid SPARQLWrapper config on initialization ([cf03808](https://github.com/lu-pl/sparqlx/commit/cf03808b4a742e18a2a0f8e7031d2e257ded09c9))


### Miscellaneous Chores

* make SPARQLWrapper configuration attribues private ([5819c8d](https://github.com/lu-pl/sparqlx/commit/5819c8d93ac3cda51b5855c5f64585c52b6a6aeb))

## [0.7.0](https://github.com/lu-pl/sparqlx/compare/v0.6.1...v0.7.0) (2025-12-28)


### Features

* implement SPARQL Protocol Operation types ([b623bfa](https://github.com/lu-pl/sparqlx/commit/b623bfad83e88e8d96dd0f5a4d39f028a21f767f))


### Documentation

* add query method section to README ([835b0dc](https://github.com/lu-pl/sparqlx/commit/835b0dc5c32bbcf85ca3c0a983b28d470334e3be))

## [0.6.1](https://github.com/lu-pl/sparqlx/compare/v0.6.0...v0.6.1) (2025-12-21)


### Bug Fixes

* propagate exceptions in ClientManager.context/.acontext ([932006e](https://github.com/lu-pl/sparqlx/commit/932006e1ea731c809cec81ce5cdb1c51fbd38389))

## [0.6.0](https://github.com/lu-pl/sparqlx/compare/v0.5.2...v0.6.0) (2025-12-17)


### Features

* add SPARQLParseException for signalling parsing failure ([94f378d](https://github.com/lu-pl/sparqlx/commit/94f378ddfef766a69b0a9c41d62626745b891072))
* add SPARQLQueryTypeLiteral type ([3ec7a82](https://github.com/lu-pl/sparqlx/commit/3ec7a828f91e972357bfe067c67d2a50a4d9b3f0))

## [0.5.2](https://github.com/lu-pl/sparqlx/compare/v0.5.1...v0.5.2) (2025-12-11)


### Bug Fixes

* implement exceptional state handling in ClientManager contexts ([858b023](https://github.com/lu-pl/sparqlx/commit/858b0231069369f01185f6600bfa747bb9d18235))

## [0.5.0](https://github.com/lu-pl/sparqlx/compare/v0.4.0...v0.5.0) (2025-12-07)


### ⚠ BREAKING CHANGES

* reorganize types module

### Features

* reorganize types module ([735e291](https://github.com/lu-pl/sparqlx/commit/735e291eb3b564ca8faebd2be047d48ef43b1634))


### Documentation

* add contribution guide ([4357e81](https://github.com/lu-pl/sparqlx/commit/4357e81d3fb107df62029268f298cfd34240aedc))

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
