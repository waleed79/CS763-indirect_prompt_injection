"""Check defense module loads correctly."""
import sys
sys.path.insert(0, '.')
from rag.defense import FusedDefense, SingleSignalDefense
print('Defense module imports OK')
fd = FusedDefense(models_dir='models')
print('FusedDefense loaded OK')
sd = SingleSignalDefense(signal='bert', models_dir='models')
print('SingleSignalDefense (bert) loaded OK')
