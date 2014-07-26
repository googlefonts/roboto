
const char *ps_prolog;
const char *ps_postlog;

bezctx *new_bezctx_ps(FILE *f);

void
bezctx_ps_close(bezctx *bc);
