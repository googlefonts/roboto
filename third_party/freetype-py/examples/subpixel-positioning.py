#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  FreeType high-level python API - Copyright 2011 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
#
# -----------------------------------------------------------------------------
'''
Subpixel rendering AND positioning using OpenGL and shaders.

'''
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
from texture_font import TextureFont, TextureAtlas
from shader import Shader


vert='''
uniform sampler2D texture;
uniform vec2 pixel;
attribute float modulo;
varying float m;
void main() {
    gl_FrontColor = gl_Color;
    gl_TexCoord[0].xy = gl_MultiTexCoord0.xy;
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    m = modulo;
}
'''

frag='''
uniform sampler2D texture;
uniform vec2 pixel;
varying float m;
void main() {
    float gamma = 1.0;

    vec2 uv      = gl_TexCoord[0].xy;
    vec4 current = texture2D(texture, uv);
    vec4 previous= texture2D(texture, uv+vec2(-1,0)*pixel);

    current  = pow(current,  vec4(1.0/gamma));
    previous = pow(previous, vec4(1.0/gamma));

    float r = current.r;
    float g = current.g;
    float b = current.b;
    float a = current.a;
    if( m <= 0.333 )
    {
        float z = m/0.333;
        r = mix(current.r, previous.b, z);
        g = mix(current.g, current.r,  z);
        b = mix(current.b, current.g,  z);
    } 
    else if( m <= 0.666 )
    {
        float z = (m-0.33)/0.333;
        r = mix(previous.b, previous.g, z);
        g = mix(current.r,  previous.b, z);
        b = mix(current.g,  current.r,  z);
    }
   else if( m < 1.0 )
    {
        float z = (m-0.66)/0.334;
        r = mix(previous.g, previous.r, z);
        g = mix(previous.b, previous.g, z);
        b = mix(current.r,  previous.b, z);
    }

   float t = max(max(r,g),b);
   vec4 color = vec4(0.,0.,0., (r+g+b)/2.);
   color = t*color + (1.-t)*vec4(r,g,b, min(min(r,g),b));
   gl_FragColor = vec4( color.rgb, color.a);
}
'''





class Label:
    def __init__(self, text, font, color=(1.0, 1.0, 1.0, 0.0),  x=0, y=0,
                 width=None, height=None, anchor_x='left', anchor_y='baseline'):
        self.text = text
        self.vertices = np.zeros((len(text)*4,3), dtype=np.float32)
        self.indices  = np.zeros((len(text)*6, ), dtype=np.uint)
        self.colors   = np.zeros((len(text)*4,4), dtype=np.float32)
        self.texcoords= np.zeros((len(text)*4,2), dtype=np.float32)
        self.attrib   = np.zeros((len(text)*4,1), dtype=np.float32)
        pen = [x,y]
        prev = None

        for i,charcode in enumerate(text):
            glyph = font[charcode]
            kerning = glyph.get_kerning(prev)
            x0 = pen[0] + glyph.offset[0] + kerning
            dx = x0-int(x0)
            x0 = int(x0)
            y0 = pen[1] + glyph.offset[1]
            x1 = x0 + glyph.size[0]
            y1 = y0 - glyph.size[1]
            u0 = glyph.texcoords[0]
            v0 = glyph.texcoords[1]
            u1 = glyph.texcoords[2]
            v1 = glyph.texcoords[3]

            index     = i*4
            indices   = [index, index+1, index+2, index, index+2, index+3]
            vertices  = [[x0,y0,1],[x0,y1,1],[x1,y1,1], [x1,y0,1]]
            texcoords = [[u0,v0],[u0,v1],[u1,v1], [u1,v0]]
            colors    = [color,]*4

            self.vertices[i*4:i*4+4] = vertices
            self.indices[i*6:i*6+6] = indices
            self.texcoords[i*4:i*4+4] = texcoords
            self.colors[i*4:i*4+4] = colors
            self.attrib[i*4:i*4+4] = dx
            pen[0] = pen[0]+glyph.advance[0]/64.0 + kerning
            pen[1] = pen[1]+glyph.advance[1]/64.0
            prev = charcode

        width = pen[0]-glyph.advance[0]/64.0+glyph.size[0]

        if anchor_y == 'top':
            dy = -round(font.ascender)
        elif anchor_y == 'center':
            dy = +round(-font.height/2-font.descender)
        elif anchor_y == 'bottom':
            dy = -round(font.descender)
        else:
            dy = 0

        if anchor_x == 'right':
            dx = -width/1.0
        elif anchor_x == 'center':
            dx = -width/2.0
        else:
            dx = 0
        self.vertices += (round(dx), round(dy), 0)


    def draw(self):
        gl.glEnable( gl.GL_TEXTURE_2D )
        gl.glDisable( gl.GL_DEPTH_TEST )

        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)
        gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)

        gl.glVertexPointer(3, gl.GL_FLOAT, 0, self.vertices)
        gl.glColorPointer(4, gl.GL_FLOAT, 0, self.colors)
        gl.glTexCoordPointer(2, gl.GL_FLOAT, 0, self.texcoords)

        r,g,b = 0,0,0
        gl.glColor( 1, 1, 1, 1 )
        gl.glEnable( gl.GL_BLEND )
        #gl.glBlendFunc( gl.GL_CONSTANT_COLOR_EXT,  gl.GL_ONE_MINUS_SRC_COLOR )
        #gl.glBlendColor(r,g,b,1)
        gl.glBlendFunc( gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA )
        gl.glBlendColor( 1, 1, 1, 1 )

        gl.glEnableVertexAttribArray( 1 );
        gl.glVertexAttribPointer( 1, 1, gl.GL_FLOAT, gl.GL_FALSE, 0, self.attrib)
        shader.bind()
        shader.uniformi('texture', 0)
        shader.uniformf('pixel', 1.0/512, 1.0/512)
        gl.glDrawElements(gl.GL_TRIANGLES, len(self.indices),
                          gl.GL_UNSIGNED_INT, self.indices)
        shader.unbind()
        gl.glDisableVertexAttribArray( 1 );
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_TEXTURE_COORD_ARRAY)
        gl.glDisable( gl.GL_TEXTURE_2D )
        gl.glDisable( gl.GL_BLEND )




if __name__ == '__main__':
    import sys

    atlas = TextureAtlas(512,512,3)

    def on_display( ):
        #gl.glClearColor(0,0,0,1)
        gl.glClearColor(1,1,1,1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glBindTexture( gl.GL_TEXTURE_2D, atlas.texid )
        for label in labels:
            label.draw()

        gl.glColor(0,0,0,1)
        gl.glBegin(gl.GL_LINES)
        gl.glVertex2i(15,0)
        gl.glVertex2i(15, 330)
        gl.glVertex2i(225, 0)
        gl.glVertex2i(225, 330)
        gl.glEnd()
        glut.glutSwapBuffers( )

    def on_reshape( width, height ):
        gl.glViewport( 0, 0, width, height )
        gl.glMatrixMode( gl.GL_PROJECTION )
        gl.glLoadIdentity( )
        gl.glOrtho( 0, width, 0, height, -1, 1 )
        gl.glMatrixMode( gl.GL_MODELVIEW )
        gl.glLoadIdentity( )

    def on_keyboard( key, x, y ):
        if key == '\033':
            sys.exit( )

    glut.glutInit( sys.argv )
    glut.glutInitDisplayMode( glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH )
    glut.glutCreateWindow( "Freetype OpenGL" )
    glut.glutReshapeWindow( 240, 330 )
    glut.glutDisplayFunc( on_display )
    glut.glutReshapeFunc( on_reshape )
    glut.glutKeyboardFunc( on_keyboard )

    font = TextureFont(atlas, './Arial.ttf', 9)
    text = "|... A Quick Brown Fox Jumps Over The Lazy Dog"
    labels = []
    x,y = 20,310
    for i in range(30):
        labels.append(Label(text=text, font=font, x=x, y=y))
        x += 0.1000000000001
        y -= 10
    atlas.upload()
    shader = Shader(vert,frag)
    glut.glutMainLoop( )
