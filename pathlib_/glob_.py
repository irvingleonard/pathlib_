#!python
"""
Unix style pathname pattern expansion

This is a backport from newer versions of the module (currently Python 3.13.0).
"""

import os.path
import re

from pathlib_.fnmatch_ import _translate as fnmatch_translate

def translate(pat, *, recursive=False, include_hidden=False, seps=None):
	"""Translate a pathname with shell wildcards to a regular expression.

	If `recursive` is true, the pattern segment '**' will match any number of path segments.

	If `include_hidden` is true, wildcards can match path segments beginning with a dot ('.').

	If a sequence of separator characters is given to `seps`, they will be used to split the pattern into segments and match path separators. If not given, os.path.sep and os.path.altsep (where available) are used.
	"""
	if not seps:
		if os.path.altsep:
			seps = (os.path.sep, os.path.altsep)
		else:
			seps = os.path.sep
	escaped_seps = ''.join(map(re.escape, seps))
	any_sep = f'[{escaped_seps}]' if len(seps) > 1 else escaped_seps
	not_sep = f'[^{escaped_seps}]'
	if include_hidden:
		one_last_segment = f'{not_sep}+'
		one_segment = f'{one_last_segment}{any_sep}'
		any_segments = f'(?:.+{any_sep})?'
		any_last_segments = '.*'
	else:
		one_last_segment = f'[^{escaped_seps}.]{not_sep}*'
		one_segment = f'{one_last_segment}{any_sep}'
		any_segments = f'(?:{one_segment})*'
		any_last_segments = f'{any_segments}(?:{one_last_segment})?'

	results = []
	parts = re.split(any_sep, pat)
	last_part_idx = len(parts) - 1
	for idx, part in enumerate(parts):
		if part == '*':
			results.append(one_segment if idx < last_part_idx else one_last_segment)
		elif recursive and part == '**':
			if idx < last_part_idx:
				if parts[idx + 1] != '**':
					results.append(any_segments)
			else:
				results.append(any_last_segments)
		else:
			if part:
				if not include_hidden and part[0] in '*?':
					results.append(r'(?!\.)')
				results.extend(fnmatch_translate(part, f'{not_sep}*', not_sep))
			if idx < last_part_idx:
				results.append(any_sep)
	res = ''.join(results)
	return fr'(?s:{res})\Z'