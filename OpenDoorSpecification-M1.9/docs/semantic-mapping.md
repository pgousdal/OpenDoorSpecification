# Semantic API mapping

M1.8 maps historical symbols to ODS operations. Symbol equality is not semantic equality:
calling convention declarations, language bindings, examples, and aliases may repeat the
same host operation.

Each mapping records:

- the ODS operation;
- one or more historical symbols;
- evidence confidence (`verified`, `partial`, `inferred`, or `unknown`);
- semantic review state.

All mappings in M1.8 are provisional. `verified` means the historical symbol and behavior
are supported by supplied evidence; it does not mean the complete ODS adapter is finished.
