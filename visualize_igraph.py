import time
import cairo
import igraph
from sqlite3 import dbapi2 as sqlite

WIDTH, HEIGHT = 5000, 5000
DEFAULT_VERTEX_SIZE = 9

def print_timing(func):
  def wrapper(*arg):
    t1 = time.time()
    res = func(*arg)
    t2 = time.time()
    print 'Done in %0.3f s' % (t2 - t1)
    return res
  return wrapper

def add_vertices(g):
  cur.execute("SELECT * FROM team")
  
  teams = {}
  for x in cur.fetchall():
    teams[x[0]] = x[1]
  g.add_vertices(len(teams) - 1)

  for v in g.vs:
    v['color'] = 'darkred'
    v['label'] = teams[v.index + 1]
    v['label_dist'] = 0
    v['label_color'] = 'white'
    v['size'] = DEFAULT_VERTEX_SIZE

  print 'Added %d vertices.' % g.vcount()

def add_edges(g):
  edges = []
  weights = []
  cur.execute("SELECT * FROM game")
  for x in cur.fetchall():
    edges.append((x[5] - 1, x[6] - 1)) # home->away edge
    weights.append(x[10]) # home->away edge weight is away's points scored
    edges.append((x[6] - 1, x[5] - 1)) # away->home edge
    weights.append(x[9]) # away->home edge weight is home's points scored
  con.commit()
  
  g.add_edges(edges)
  for e in g.es:
    g.vs[e.source]['size'] += 1 # all edges are double, so only source vertex is increased
    e['width'] = 0.8
    e['color'] = 'orange'
    e['weight'] = weights[e.index]

  print 'Added %d edges.' % g.ecount()
  return weights

@print_timing
def draw_layout(g, layout_func, surface):
  func = getattr(g, layout_func)
  print 'Calculating layout...'
  graph_layout = func()
  print 'Calculated %s.' % layout_func
  p = igraph.drawing.plot(g, target=surface, bbox=(0, 0, WIDTH, HEIGHT), layout=graph_layout)
  print 'Plot done. Saving file...'
  img_name = 'agcmpl_%s.png' % layout_func
  p.save(img_name)
  print '%s saved.' % img_name

def prepare_cairo_surface():
  surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
  ctx = cairo.Context(surface)
  ctx.scale(WIDTH / 1.0, HEIGHT / 1.0) # normalizing the canvas
  
  pattern = cairo.SolidPattern(0.0, 0.0, 0.0, 1.0)
  ctx.rectangle(0, 0, 1, 1)
  ctx.set_source(pattern)
  ctx.fill()
  
  return surface

def calculate_pagerank(g, weights=None):
  print 'Teams ranked by PageRank:'
  pr = g.pagerank(directed=True, weights=weights_list)
  f = open('teams_by_pagerank.txt', 'w')
  for i, (team, pr_value) in enumerate(sorted(zip(g.vs, pr), key=lambda x: x[1], reverse=True)):
    f.write('%3d. %-30s %6.3f %4d\n' % (i + 1, team['label'], pr_value * 1000, team['size'] - DEFAULT_VERTEX_SIZE))
    print '%3d. %-30s %6.3f %4d' % (i + 1, team['label'], pr_value * 1000, team['size'] - DEFAULT_VERTEX_SIZE)
  f.close()

if __name__ == '__main__':
  g = igraph.Graph(directed=True)

  con = sqlite.connect('agcmpl.db')
  cur = con.cursor()

  add_vertices(g)
  weights_list = add_edges(g)

  if g.is_connected():
    print 'Graph is connected.'
  else:
    print 'Graph is not connected.'

  calculate_pagerank(g, weights_list)

  print 'Simplifying graph...'
  g.to_undirected(collapse=False)
  g.simplify()
  print 'Edges after simplification:', g.ecount()

  layouts = ['layout_fruchterman_reingold', 'layout_kamada_kawai', 'layout_graphopt', 'layout_lgl', 'layout_circle']
  for layout in layouts:
    surface = prepare_cairo_surface()
    draw_layout(g, layout, surface)
