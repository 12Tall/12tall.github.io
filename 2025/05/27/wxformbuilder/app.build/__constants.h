#ifndef __NUITKA_GLOBAL_CONSTANTS_H__
#define __NUITKA_GLOBAL_CONSTANTS_H__

extern PyObject *global_constants[105];
// ()
#define const_tuple_empty global_constants[0]
// {}
#define const_dict_empty global_constants[1]
// 0
#define const_int_0 global_constants[2]
// 1
#define const_int_pos_1 global_constants[3]
// -1
#define const_int_neg_1 global_constants[4]
// 0.0
#define const_float_0_0 global_constants[5]
// -0.0
#define const_float_minus_0_0 global_constants[6]
// 1.0
#define const_float_1_0 global_constants[7]
// -1.0
#define const_float_minus_1_0 global_constants[8]
// 0
#define const_int_0 global_constants[2]
// ''
#define const_str_empty global_constants[9]
// b''
#define const_bytes_empty global_constants[10]
// '__module__'
#define const_str_plain___module__ global_constants[11]
// '__class__'
#define const_str_plain___class__ global_constants[12]
// '__name__'
#define const_str_plain___name__ global_constants[13]
// '__package__'
#define const_str_plain___package__ global_constants[14]
// '__metaclass__'
#define const_str_plain___metaclass__ global_constants[15]
// '__abstractmethods__'
#define const_str_plain___abstractmethods__ global_constants[16]
// '__closure__'
#define const_str_plain___closure__ global_constants[17]
// '__dict__'
#define const_str_plain___dict__ global_constants[18]
// '__doc__'
#define const_str_plain___doc__ global_constants[19]
// '__file__'
#define const_str_plain___file__ global_constants[20]
// '__path__'
#define const_str_plain___path__ global_constants[21]
// '__enter__'
#define const_str_plain___enter__ global_constants[22]
// '__exit__'
#define const_str_plain___exit__ global_constants[23]
// '__builtins__'
#define const_str_plain___builtins__ global_constants[24]
// '__all__'
#define const_str_plain___all__ global_constants[25]
// '__init__'
#define const_str_plain___init__ global_constants[26]
// '__cmp__'
#define const_str_plain___cmp__ global_constants[27]
// '__iter__'
#define const_str_plain___iter__ global_constants[28]
// '__loader__'
#define const_str_plain___loader__ global_constants[29]
// '__compiled__'
#define const_str_plain___compiled__ global_constants[30]
// '__nuitka__'
#define const_str_plain___nuitka__ global_constants[31]
// 'inspect'
#define const_str_plain_inspect global_constants[32]
// 'compile'
#define const_str_plain_compile global_constants[33]
// 'range'
#define const_str_plain_range global_constants[34]
// 'open'
#define const_str_plain_open global_constants[35]
// 'super'
#define const_str_plain_super global_constants[36]
// 'sum'
#define const_str_plain_sum global_constants[37]
// 'format'
#define const_str_plain_format global_constants[38]
// '__import__'
#define const_str_plain___import__ global_constants[39]
// 'bytearray'
#define const_str_plain_bytearray global_constants[40]
// 'staticmethod'
#define const_str_plain_staticmethod global_constants[41]
// 'classmethod'
#define const_str_plain_classmethod global_constants[42]
// 'keys'
#define const_str_plain_keys global_constants[43]
// 'get'
#define const_str_plain_get global_constants[44]
// 'name'
#define const_str_plain_name global_constants[45]
// 'globals'
#define const_str_plain_globals global_constants[46]
// 'locals'
#define const_str_plain_locals global_constants[47]
// 'fromlist'
#define const_str_plain_fromlist global_constants[48]
// 'level'
#define const_str_plain_level global_constants[49]
// 'read'
#define const_str_plain_read global_constants[50]
// 'rb'
#define const_str_plain_rb global_constants[51]
// 'r'
#define const_str_plain_r global_constants[52]
// 'w'
#define const_str_plain_w global_constants[53]
// 'b'
#define const_str_plain_b global_constants[54]
// '/'
#define const_str_slash global_constants[55]
// '\\'
#define const_str_backslash global_constants[56]
// 'path'
#define const_str_plain_path global_constants[57]
// 'basename'
#define const_str_plain_basename global_constants[58]
// 'dirname'
#define const_str_plain_dirname global_constants[59]
// 'abspath'
#define const_str_plain_abspath global_constants[60]
// 'isabs'
#define const_str_plain_isabs global_constants[61]
// 'normpath'
#define const_str_plain_normpath global_constants[62]
// 'exists'
#define const_str_plain_exists global_constants[63]
// 'isdir'
#define const_str_plain_isdir global_constants[64]
// 'isfile'
#define const_str_plain_isfile global_constants[65]
// 'listdir'
#define const_str_plain_listdir global_constants[66]
// 'stat'
#define const_str_plain_stat global_constants[67]
// 'lstat'
#define const_str_plain_lstat global_constants[68]
// 'close'
#define const_str_plain_close global_constants[69]
// 'getattr'
#define const_str_plain_getattr global_constants[70]
// '__cached__'
#define const_str_plain___cached__ global_constants[71]
// 'print'
#define const_str_plain_print global_constants[72]
// 'end'
#define const_str_plain_end global_constants[73]
// 'file'
#define const_str_plain_file global_constants[74]
// 'bytes'
#define const_str_plain_bytes global_constants[75]
// '.'
#define const_str_dot global_constants[76]
// '_'
#define const_str_underscore global_constants[77]
// '__loader__'
#define const_str_plain___loader__ global_constants[29]
// 'send'
#define const_str_plain_send global_constants[78]
// 'throw'
#define const_str_plain_throw global_constants[79]
// 'site'
#define const_str_plain_site global_constants[80]
// 'type'
#define const_str_plain_type global_constants[81]
// 'len'
#define const_str_plain_len global_constants[82]
// 'range'
#define const_str_plain_range global_constants[34]
// 'repr'
#define const_str_plain_repr global_constants[83]
// 'int'
#define const_str_plain_int global_constants[84]
// 'iter'
#define const_str_plain_iter global_constants[85]
// '__spec__'
#define const_str_plain___spec__ global_constants[86]
// '_initializing'
#define const_str_plain__initializing global_constants[87]
// 'parent'
#define const_str_plain_parent global_constants[88]
// 'types'
#define const_str_plain_types global_constants[89]
// 'ascii'
#define const_str_plain_ascii global_constants[90]
// 'punycode'
#define const_str_plain_punycode global_constants[91]
// '__main__'
#define const_str_plain___main__ global_constants[92]
// 'as_file'
#define const_str_plain_as_file global_constants[93]
// 'register'
#define const_str_plain_register global_constants[94]
// '__class_getitem__'
#define const_str_plain___class_getitem__ global_constants[95]
// 'reconfigure'
#define const_str_plain_reconfigure global_constants[96]
// 'encoding'
#define const_str_plain_encoding global_constants[97]
// 'line_buffering'
#define const_str_plain_line_buffering global_constants[98]
// '__match_args__'
#define const_str_plain___match_args__ global_constants[99]
// '__aenter__'
#define const_str_plain___aenter__ global_constants[100]
// '__aexit__'
#define const_str_plain___aexit__ global_constants[101]
// 'split'
#define const_str_plain_split global_constants[102]
// 'fileno'
#define const_str_plain_fileno global_constants[103]
#endif
