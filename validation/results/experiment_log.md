# EP2 Experiment Log

## Passo 1: Conversão JSON-LD → TTL
- **Status**: ✅ PASS
- **Input**: boil-water-model.jsonld (4.470 bytes)
- **Output**: boil-water-model.ttl (124 triples RDF)
- **Método**: pyld (JSON-LD expansion + N-Quads) → rdflib (parse + serialize Turtle)
- **Observação**: O @context remoto (https://flowfram.com/ontology/fram/context.jsonld) foi substituído pelo arquivo local context.jsonld para garantir reprodutibilidade. Todos os 124 triples foram gerados com sucesso, com prefixos fram:, schema:, rdfs: e xsd: corretamente mapeados.
