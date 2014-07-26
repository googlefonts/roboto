/**
 * Misc portability and convenience macros.
 **/

#include <stdlib.h>

#define zalloc malloc
#define zrealloc realloc
#define zfree free

#define znew(type, n) (type *)zalloc(sizeof(type) * (n))
#define zrenew(type, p, n) (type *)zrealloc((p), sizeof(type) * (n))
