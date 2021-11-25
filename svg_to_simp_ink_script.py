#! /usr/bin/env python

'''
Copyright (C) 2021 Scott Pakin, scott-ink@pakin.org

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301, USA.

'''

import inkex

class SvgToPythonScript(inkex.OutputExtension):
    'Save an Inkscape image to a Simple Inkscape Scripting script.'

    def transform_arg(self, node):
        "Return an SVG node's transform string as a function argument."
        xform = node.get('transform')
        if xform == '':
            return xform
        return ', transform=%s' % repr(xform)

    def conn_avoid_arg(self, node):
        "Return an SVG node's connector-avoid value as a function argument."
        avoid = node.get('inkscape:connector-avoid')
        if avoid == '':
            return avoid
        return ', conn_avoid=%s' % repr(avoid == 'true')

    def style_args(self, node):
        "Return an SVG node's style string as key=value arguments."
        style = node.get('style')
        args = ''
        for term in style.split(';'):
            k, v = term.split(':', 1)
            k = k.replace('-', '_')
            # TODO: Pretty-print values.
            args += ', %s=%s' % (k, repr(v))
        return args

    def extra_args(self, node):
        'Return extra function arguments (transform, style) if available.'
        args = [self.transform_arg(node),
                self.conn_avoid_arg(node),
                self.style_args(node)]
        return ''.join(args)
        
    def convert_circle(self, node):
        'Return Python code for drawing a circle.'
        cx, cy, r = node.get('cx'), node.get('cy'), node.get('r')
        extra = self.extra_args(node)
        return 'circle((%s, %s), %s%s)' % (cx, cy, r, extra)
        
    def convert_ellipse(self, node):
        'Return Python code for drawing an ellipse.'
        cx, cy = node.get('cx'), node.get('cy')
        rx, ry = node.get('rx'), node.get('ry')
        extra = self.extra_args(node)
        return 'ellipse((%s, %s), (%s, %s)%s)' % (cx, cy, rx, ry, extra)
        
    def convert_all_shapes(self):
        'Convert each SVG shape to a Python function call.'
        code = []
        for node in self.svg.xpath('//svg:circle | //svg:ellipse'):
            if isinstance(node, inkex.Circle):
                code.append(self.convert_circle(node))
            elif isinstance(node, inkex.Ellipse):
                code.append(self.convert_ellipse(node))
        return code
    
    def save(self, stream):
        'Write Python code that regenerates the SVG to an output stream.'
        stream.write(b'''\
# This script is intended to be run from Inkscape's Simple Inkscape
# Scripting extension.

''')
        for code in self.convert_all_shapes():
            ln = code + '\n'
            stream.write(ln.encode('utf-8'))


if __name__ == '__main__':
    SvgToPythonScript().run()
