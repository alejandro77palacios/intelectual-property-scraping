from pathlib import Path

import camelot
import matplotlib.pyplot as plt

path = '/Users/alejandropalacios/programacion/freelancer/ipindia/2010/2010-01-01/pdf/Part-I.pdf'
tables = camelot.read_pdf(Path(path),
                          pages='3',
                          table_areas=['50,700,600,100'],
                          edge_tol=500,
                          columns=['410'],
                          row_tol=15,
                          flavor='stream')
camelot.plot(tables[0], kind='contour')
plt.show()
df = tables[0].df
subject_index = df[df.iloc[:, 0].str.contains('Subject', na=False, case=False)].index[0]
df = df[subject_index:]
df.columns = df.iloc[0]
df = df[1:]
