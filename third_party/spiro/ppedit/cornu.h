void
cornu_to_bpath(const double xs[], const double ys[], const double ths[], int n,
	       bezctx *bc, double tol, int closed, int kt0, int n_kt);

void
local_ths(const double xs[], const double ys[], double ths[], int n, int closed);

void
endpoint_ths(const double xs[], const double ys[], double ths[], int n);

void
tweak_ths(const double xs[], const double ys[], double ths[], int n,
	  double delt, int closed);
