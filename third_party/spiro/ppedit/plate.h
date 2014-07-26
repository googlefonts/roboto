typedef enum {
    KT_OPEN = 1,
    KT_CORNER = 2,
    KT_LEFT = 4,
    KT_RIGHT = 8,
    KT_CORNU = 16,
    KT_SELECTED = 256
} kt_flags;

typedef struct {
    double x;
    double y;
    kt_flags flags;
} knot;

typedef struct {
    int n_kt;
    int n_kt_max;
    knot *kt;
    int closed;
} subpath;

typedef enum {
    MOUSE_MODE_SELECT,
    MOUSE_MODE_ADD_CURVE,
    MOUSE_MODE_ADD_CORNER,
    MOUSE_MODE_ADD_CORNU,
    MOUSE_MODE_ADD_LEFT,
    MOUSE_MODE_ADD_RIGHT
} mouse_mode;

typedef enum {
    MOTION_MODE_IDLE,
    MOTION_MODE_SELECT,
    MOTION_MODE_MOVE
} motion_mode;

typedef struct {
    double x0, y0;
    const char *description;

    int n_sp;
    int n_sp_max;
    subpath *sp;
    mouse_mode mmode;
    mouse_mode last_curve_mmode;
    motion_mode motmode;
    double sel_x0, sel_y0;
} plate;

typedef enum {
    PRESS_MOD_SHIFT = 1,
    PRESS_MOD_CTRL = 2,
    PRESS_MOD_DOUBLE = 4,
    PRESS_MOD_TRIPLE = 8
} press_mod;

plate *
new_plate(void);

void
free_plate(plate *p);

plate *
copy_plate(const plate *p);

void
plate_select_all(plate *p, int selected);

subpath *
plate_find_selected_sp(plate *p);

subpath *
plate_new_sp(plate *p);

void
plate_press(plate *p, double x, double y, press_mod mods);

void
plate_motion_move(plate *p, double x, double y);

void
plate_motion_select(plate *p, double x, double y);

void plate_unpress(plate *p);

void
plate_toggle_corner(plate *p);

void
plate_delete_pt(plate *p);

spiro_seg *
draw_subpath(const subpath *sp, bezctx *bc);

int
file_write_plate(const char *fn, const plate *p);

plate *
file_read_plate(const char *fn);
