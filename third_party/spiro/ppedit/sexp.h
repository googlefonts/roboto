typedef struct {
    FILE *f;
    char tokbuf[256];
    int singlechar;
    int is_double;
    double d;
} sexp_reader;

int
sexp_token(sexp_reader *sr);
