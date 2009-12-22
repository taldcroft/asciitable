a = """
fname : file or str [Inputter]

 File or filename to read. If the filename extension is gz or bz2, the file is
 first decompressed.

dtype : dtype, optional [Outputter]

 Data type of the resulting array. If None, the dtypes will be determined by
 the contents of each column, individually.

comments : str, optional [Header, Data]

 The character used to indicate the start of a comment. All the characters
 occurring on a line after a comment are discarded

delimiter : str, int, or sequence, optional [Splitter]

 The string used to separate values. By default, any consecutive whitespaces
 act as delimiter. An integer or sequence of integers can also be provided as
 width(s) of each field.

skip_header : int, optional [Header, Data]

 The numbers of lines to skip at the beginning of the file.

skip_footer : int, optional [Data]

 The numbers of lines to skip at the end of the file

converters : variable or None, optional [Outputter]

 The set of functions that convert the data of a column to a value. The
 converters can also be used to provide a default value for missing data:
 converters = {3: lambda s: float(s or 0)}.

missing_values : variable or None, optional [?]

 The set of strings corresponding to missing data.

filling_values : variable or None, optional [?]

 The set of values to be used as default when the data are missing.

usecols : sequence or None, optional [Header]

 Which columns to read, with 0 being the first. For example, usecols = (1, 4,
 5) will extract the 2nd, 5th and 6th columns.

names : {None, True, str, sequence}, optional [Header]

 If names is True, the field names are read from the first valid line after the
 first skiprows lines. If names is a sequence or a single-string of
 comma-separated names, the names will be used to define the field names in a
 structured dtype. If names is None, the names of the dtype fields will be
 used, if any.

excludelist : sequence, optional [Header]

 A list of names to exclude. 

deletechars : str, optional [not needed]

 A string combining invalid characters that must be deleted from the names.

defaultfmt : str, optional [Header]

 A format used to define default field names, such as f%i or f_%02i.

autostrip : bool, optional [Splitter]

 Whether to automatically strip white spaces from the variables.

case_sensitive : {True, False, upper, lower}, optional [Header]

 If True, field names are case sensitive. If False or upper, field names are
 converted to upper case. If lower, field names are converted to lower case.

unpack : bool, optional [Outputter]

 If True, the returned array is transposed, so that arguments may be unpacked
 using x, y, z = loadtxt(...)

usemask : bool, optional [Outputter]

 If True, return a masked array. If False, return a regular array.

invalid_raise : bool, optional [skip]

 If True, an exception is raised if an inconsistency is detected in the number
 of columns. If False, a warning is emitted and the offending lines are
 skipped.
"""
