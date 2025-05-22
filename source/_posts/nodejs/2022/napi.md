---
title: N-api
date: 2022-08-03  
tags:   
    - c/cpp  
    - nodeJS    
    - N-api
---  

仅记录对`N-api` 的使用方法以及函数签名。***在`Windows` 平台下，如果我们安装的是32 位的Nodejs，`N-api` 应该是生成`32` 位的`.node` 文件，而且并没有启用`UNICODE` 的支持，即所有`_WIN64, UNICODE` 下的宏定义都是无效的***。所以在Winodws 版本下的API 函数最好都调用`A` 结尾的。  
<!-- more -->
<CodeGroup>
<CodeGroupItem title=".node 位宽验证">

```c{7,13-14}
// 在Windows 系统下编译程序时，会针对目标平台改变某些宏定义。
// 据此，我们可以输出这些结果，来判断编译结果的目标位宽
#ifndef SIZE_MAX
  #ifdef _WIN64
 #define SIZE_MAX 0xffffffffffffffffui64
  #else
 #define SIZE_MAX 0xffffffffui32
  #endif
#endif

// 而napi 自身的宏定义中，也只有关于_WIN32 的声明
#ifndef NAPI_EXTERN
  #ifdef _WIN32
  #define NAPI_EXTERN __declspec(dllexport)
  #elif defined(__wasm32__)
  #define NAPI_EXTERN __attribute__((visibility("default")))  \  __attribute__((__import_module__("napi")))
  #else
  #define NAPI_EXTERN __attribute__((visibility("default")))
  #endif
#endif
```

</CodeGroupItem>
</CodeGroup>



## 一般函数  

最原始的`N-api` 的代码是`C` 风格的。所以函数的调用也都是面向过程的风格，写起来会比较啰嗦。

<CodeGroup>
<CodeGroupItem title="代码模板">

```c{15-16}
#include <assert.h>
#include <node_api.h>
/**
* 函数：n-api 的函数一般由五部分组成  
* - 函数名。一般用static 修饰符
* - 形参1：napi_env。用于获取函数调用时的环境
* - 形参2：napi_callback_info。用于传递函数调用时的实参
* - 返回值：napi_value。napi 中所有的数据都使用napi_value 封装 
* - 运行状态：napi_status。通过assert 断言函数运行状态
*/
static napi_value Method(napi_env env, napi_callback_info info) {
  napi_status status;
  napi_value world;
  // 这里我修改了示例代码，用来验证编译的目标平台是32 位的
  // status = napi_create_string_utf8(env, "world", 5, &world);
  status = napi_create_bigint_int64(env, NAPI_AUTO_LENGTH, &world);
  assert(status == napi_ok);  // 运行结果断言
  return world;
}

/** 对象属性的描述符，这条宏命令最终被解释为下面结构体：
* typedef struct {
*  // utf8name or name 应该至少有一个为空.
*  const char* utf8name;  // name
*  napi_value name;  // 0:NULL
*
*  napi_callback method;  // func 函数的指针
*  napi_callback getter;  // 0:NULL
*  napi_callback setter;  // 0:NULL
*  napi_value value; // 0:NULL
*
*  napi_property_attributes attributes;  // 对应默认、可写、可枚举、可配置的属性
*  void* data; // 0:NULL
*} napi_property_descriptor;
*/
#define DECLARE_NAPI_METHOD(name, func) \
  { name, 0, func, 0, 0, 0, napi_default, 0 }
// 一个普通函数描述符的结构体

/**
* 初始化函数。需要接收exports 对象，进行修改后再返回
*
* 定义JS 对象属性：
* napi_define_properties(napi_env env, // 
* napi_value object, // 被操作的对象
* size_t property_count, // 属性（数组内元素）数量
* const napi_property_descriptor* properties);  
* // 属性描述符（数组）的指针
* 其实这里对应的是一个属性数组与其内部元素的数量。
*/
static napi_value Init(napi_env env, napi_value exports) {
  napi_status status;
  napi_property_descriptor desc = DECLARE_NAPI_METHOD("hello", Method);
  status = napi_define_properties(env, exports, 1, &desc);
  assert(status == napi_ok);
  return exports;
}

// 最终注册插件的宏命令，一般保持默认即可
NAPI_MODULE(NODE_GYP_MODULE_NAME, Init)
```
</CodeGroupItem>
<CodeGroupItem title="状态码">

```c
typedef enum {
  napi_ok,
  napi_invalid_arg,
  napi_object_expected,
  napi_string_expected,
  napi_name_expected,
  napi_function_expected,
  napi_number_expected,
  napi_boolean_expected,
  napi_array_expected,
  napi_generic_failure,
  napi_pending_exception,
  napi_cancelled,
  napi_escape_called_twice,
  napi_handle_scope_mismatch,
  napi_callback_scope_mismatch,
  napi_queue_full,
  napi_closing,
  napi_bigint_expected,
  napi_date_expected,
  napi_arraybuffer_expected,
  napi_detachable_arraybuffer_expected,
  napi_would_deadlock  // unused
} napi_status;
```

</CodeGroupItem>
</CodeGroup>


## 一般数据  
好像我们并不能看到`N-api` 中关于数据的具体定义，但是这并不影响我们可以通过一系列的函数来构造或者解析`JS` 数据。虽然下面的代码看起来很多很吓人，但无外乎数据的获取、转换、设置，在JS 中，函数也是一种数据。    
**一般在调用`napi` 函数时，返回值都是`napi_status` 类型，所以需要预先声明一个`napi_vlaue` 用来存储函数返回值，具体操作为在调用函数时将传入返回值的指针**

::: details 数据处理的方法
```c
// 经过实验得知：
// napi 插件开发是基于32 位的，也就是说_WIN64 下定义的类型是不适用的
//  0xffffffffui32
#define NAPI_AUTO_LENGTH SIZE_MAX  

// 获取更详细的运行数据
napi_get_last_error_info(napi_env env, const napi_extended_error_info** result);

// Getters for defined singletons/个人理解为获取预定义的数据类型
NAPI_EXTERN napi_status napi_get_undefined(napi_env env, napi_value* result);
NAPI_EXTERN napi_status napi_get_null(napi_env env, napi_value* result);
NAPI_EXTERN napi_status napi_get_global(napi_env env, napi_value* result);
NAPI_EXTERN napi_status napi_get_boolean(napi_env env, bool value, napi_value* result);

// 创建原始对象或方法。一般来说是需要传入具体数据的，如果没有传入的话，默认就是空对象
NAPI_EXTERN napi_status napi_create_object(napi_env env, napi_value* result);
NAPI_EXTERN napi_status napi_create_array(napi_env env, napi_value* result);
NAPI_EXTERN napi_status napi_create_array_with_length(napi_env env, size_t length, napi_value* result);
NAPI_EXTERN napi_status napi_create_double(napi_env env, double value, napi_value* result);
NAPI_EXTERN napi_status napi_create_int32(napi_env env, int32_t value, napi_value* result);
NAPI_EXTERN napi_status napi_create_uint32(napi_env env, uint32_t value, napi_value* result);
NAPI_EXTERN napi_status napi_create_int64(napi_env env, int64_t value, napi_value* result);
NAPI_EXTERN napi_status napi_create_string_latin1(napi_env env, const char* str, size_t length, napi_value* result);
NAPI_EXTERN napi_status napi_create_string_utf8(napi_env env, const char* str, size_t length, napi_value* result);
NAPI_EXTERN napi_status napi_create_string_utf16(napi_env env, const char16_t* str, size_t length, napi_value* result);
NAPI_EXTERN napi_status napi_create_symbol(napi_env env, napi_value description, napi_value* result);
NAPI_EXTERN napi_status napi_create_function(napi_env env, const char* utf8name, size_t length, napi_callback cb, void* data, napi_value* result);
NAPI_EXTERN napi_status napi_create_error(napi_env env, napi_value code, napi_value msg, napi_value* result);
NAPI_EXTERN napi_status napi_create_type_error(napi_env env, napi_value code, napi_value msg, napi_value* result);
NAPI_EXTERN napi_status napi_create_range_error(napi_env env, napi_value code, napi_value msg, napi_value* result);


/**
* 获取原始数据类型的方法
* typedef enum {
*  // ES6 types (corresponds to typeof)
*  napi_undefined,
*  napi_null,
*  napi_boolean,
*  napi_number,
*  napi_string,
*  napi_symbol,
*  napi_object,
*  napi_function,
*  napi_external,
*  napi_bigint,
*} napi_valuetype;
*/
NAPI_EXTERN napi_status napi_typeof(napi_env env, napi_value value, napi_valuetype* result);

// 从JS 数据提取C 兼容的数据，也是要预先声明返回值的
NAPI_EXTERN napi_status napi_get_value_double(napi_env env, napi_value value, double* result);
NAPI_EXTERN napi_status napi_get_value_int32(napi_env env, napi_value value, int32_t* result);
NAPI_EXTERN napi_status napi_get_value_uint32(napi_env env, napi_value value, uint32_t* result);
NAPI_EXTERN napi_status napi_get_value_int64(napi_env env, napi_value value, int64_t* result);
NAPI_EXTERN napi_status napi_get_value_bool(napi_env env, napi_value value, bool* result);

// 字符串处理
// 拷贝???? 编码的字符串到缓冲区
NAPI_EXTERN napi_status napi_get_value_string_latin1(napi_env env, napi_value value, char* buf, size_t bufsize, size_t* result);
NAPI_EXTERN napi_status napi_get_value_string_utf8(napi_env env, napi_value value, char* buf, size_t bufsize, size_t* result);
NAPI_EXTERN napi_status napi_get_value_string_utf16(napi_env env, napi_value value, char16_t* buf, size_t bufsize, size_t* result);
// 强制类型转换？
// Methods to coerce values
// These APIs may execute user scripts
NAPI_EXTERN napi_status napi_coerce_to_bool(napi_env env, napi_value value, napi_value* result);
NAPI_EXTERN napi_status napi_coerce_to_number(napi_env env, napi_value value, napi_value* result);
NAPI_EXTERN napi_status napi_coerce_to_object(napi_env env, napi_value value, napi_value* result);
NAPI_EXTERN napi_status napi_coerce_to_string(napi_env env, napi_value value, napi_value* result);

// 操作对象的方法
NAPI_EXTERN napi_status napi_get_prototype(napi_env env, napi_value object, napi_value* result);
NAPI_EXTERN napi_status napi_get_property_names(napi_env env, napi_value object, napi_value* result);
NAPI_EXTERN napi_status napi_set_property(napi_env env, napi_value object, napi_value key, napi_value value);
NAPI_EXTERN napi_status napi_has_property(napi_env env, napi_value object, napi_value key, bool* result);
NAPI_EXTERN napi_status napi_get_property(napi_env env, napi_value object, napi_value key, napi_value* result);
NAPI_EXTERN napi_status napi_delete_property(napi_env env, napi_value object, napi_value key, bool* result);
NAPI_EXTERN napi_status napi_has_own_property(napi_env env, napi_value object, napi_value key, bool* result);
NAPI_EXTERN napi_status napi_set_named_property(napi_env env, napi_value object, const char* utf8name, napi_value value);
NAPI_EXTERN napi_status napi_has_named_property(napi_env env, napi_value object, const char* utf8name, bool* result);
NAPI_EXTERN napi_status napi_get_named_property(napi_env env, napi_value object, const char* utf8name, napi_value* result);
NAPI_EXTERN napi_status napi_set_element(napi_env env, napi_value object, uint32_t index, napi_value value);
NAPI_EXTERN napi_status napi_has_element(napi_env env, napi_value object, uint32_t index, bool* result);
NAPI_EXTERN napi_status napi_get_element(napi_env env, napi_value object, uint32_t index, napi_value* result);
NAPI_EXTERN napi_status napi_delete_element(napi_env env, napi_value object, uint32_t index, bool* result);

// 定义对象属性
napi_define_properties(napi_env env, napi_value object, size_t property_count, const napi_property_descriptor* properties);

// 操作数组的方法
NAPI_EXTERN napi_status napi_is_array(napi_env env, napi_value value, bool* result);
NAPI_EXTERN napi_status napi_get_array_length(napi_env env, napi_value value, uint32_t* result);

// 数据比较的方法
NAPI_EXTERN napi_status napi_strict_equals(napi_env env, napi_value lhs, napi_value rhs, bool* result);

// 操作函数的方法
NAPI_EXTERN napi_status napi_call_function(napi_env env, napi_value recv, napi_value func, size_t argc, const napi_value* argv, napi_value* result);
NAPI_EXTERN napi_status napi_new_instance(napi_env env, napi_value constructor, size_t argc, const napi_value* argv, napi_value* result);
NAPI_EXTERN napi_status napi_instanceof(napi_env env, napi_value object, napi_value constructor, bool* result);


NAPI_EXTERN napi_status napi_get_new_target(napi_env env, napi_callback_info cbinfo, napi_value* result);
NAPI_EXTERN napi_status napi_define_class(napi_env env, const char* utf8name, size_t length, napi_callback constructor, void* data, size_t property_count, const napi_property_descriptor* properties, napi_value* result);

// 封装扩展数据类型
NAPI_EXTERN napi_status napi_wrap(napi_env env, napi_value js_object, void* native_object, napi_finalize finalize_cb, void* finalize_hint, napi_ref* result);
NAPI_EXTERN napi_status napi_unwrap(napi_env env, napi_value js_object, void** result);
NAPI_EXTERN napi_status napi_remove_wrap(napi_env env, napi_value js_object, void** result);
NAPI_EXTERN napi_status napi_create_external(napi_env env, void* data, napi_finalize finalize_cb, void* finalize_hint, napi_value* result);
NAPI_EXTERN napi_status napi_get_value_external(napi_env env, napi_value value, void** result);

// 控制对象生命周期
// 这里的操作要比较小心，目测会有内存泄漏的风险

// 设置一个对象的引用
// Set initial_refcount to 0 for a weak reference, >0 for a strong reference.
NAPI_EXTERN napi_status napi_create_reference(napi_env env, napi_value value, uint32_t initial_refcount, napi_ref* result);
// 删除对象的引用
// Deletes a reference. The referenced value is released, and may
// be GC'd unless there are other references to it.
NAPI_EXTERN napi_status napi_delete_reference(napi_env env, napi_ref ref);

// Increments the reference count, optionally returning the resulting count.
// After this call the  reference will be a strong reference because its
// refcount is >0, and the referenced object is effectively "pinned".
// Calling this when the refcount is 0 and the object is unavailable
// results in an error.
NAPI_EXTERN napi_status napi_reference_ref(napi_env env, napi_ref ref, uint32_t* result);

// Decrements the reference count, optionally returning the resulting count.
// If the result is 0 the reference is now weak and the object may be GC'd
// at any time if there are no other references. Calling this when the
// refcount is already 0 results in an error.
NAPI_EXTERN napi_status napi_reference_unref(napi_env env, napi_ref ref, uint32_t* result);

// Attempts to get a referenced value. If the reference is weak,
// the value might no longer be available, in that case the call
// is still successful but the result is NULL.
NAPI_EXTERN napi_status napi_get_reference_value(napi_env env, napi_ref ref, napi_value* result);
NAPI_EXTERN napi_status napi_open_handle_scope(napi_env env, napi_handle_scope* result);
NAPI_EXTERN napi_status napi_close_handle_scope(napi_env env, napi_handle_scope scope);
NAPI_EXTERN napi_status napi_open_escapable_handle_scope(napi_env env, napi_escapable_handle_scope* result);
NAPI_EXTERN napi_status napi_close_escapable_handle_scope(napi_env env, napi_escapable_handle_scope scope);
NAPI_EXTERN napi_status napi_escape_handle(napi_env env, napi_escapable_handle_scope scope, napi_value escapee, napi_value* result);

// 异常处理
NAPI_EXTERN napi_status napi_throw(napi_env env, napi_value error);
NAPI_EXTERN napi_status napi_throw_error(napi_env env, const char* code, const char* msg);
NAPI_EXTERN napi_status napi_throw_type_error(napi_env env, const char* code, const char* msg);
NAPI_EXTERN napi_status napi_throw_range_error(napi_env env, const char* code, const char* msg);
NAPI_EXTERN napi_status napi_is_error(napi_env env, napi_value value, bool* result);

// 异常捕获
NAPI_EXTERN napi_status napi_is_exception_pending(napi_env env, bool* result);
NAPI_EXTERN napi_status napi_get_and_clear_last_exception(napi_env env, napi_value* result);

// 数组Buffer 和确定类型的数组
NAPI_EXTERN napi_status napi_is_arraybuffer(napi_env env, napi_value value, bool* result);
NAPI_EXTERN napi_status napi_create_arraybuffer(napi_env env, size_t byte_length, void** data, napi_value* result);
NAPI_EXTERN napi_status napi_create_external_arraybuffer(napi_env env, void* external_data, size_t byte_length, napi_finalize finalize_cb, void* finalize_hint, napi_value* result);
NAPI_EXTERN napi_status napi_get_arraybuffer_info(napi_env env, napi_value arraybuffer, void** data, size_t* byte_length);
NAPI_EXTERN napi_status napi_is_typedarray(napi_env env, napi_value value, bool* result);
NAPI_EXTERN napi_status napi_create_typedarray(napi_env env, napi_typedarray_type type, size_t length, napi_value arraybuffer, size_t byte_offset, napi_value* result);
NAPI_EXTERN napi_status napi_get_typedarray_info(napi_env env, napi_value typedarray, napi_typedarray_type* type, size_t* length, void** data, napi_value* arraybuffer, size_t* byte_offset);

NAPI_EXTERN napi_status napi_create_dataview(napi_env env, size_t length, napi_value arraybuffer, size_t byte_offset, napi_value* result);
NAPI_EXTERN napi_status napi_is_dataview(napi_env env, napi_value value, bool* result);
NAPI_EXTERN napi_status napi_get_dataview_info(napi_env env, napi_value dataview, size_t* bytelength, void** data, napi_value* arraybuffer, size_t* byte_offset);

// Node 版本管理
NAPI_EXTERN napi_status napi_get_version(napi_env env, uint32_t* result);

// Promises，异步
NAPI_EXTERN napi_status napi_create_promise(napi_env env, napi_deferred* deferred, napi_value* promise);
NAPI_EXTERN napi_status napi_resolve_deferred(napi_env env, napi_deferred deferred, napi_value resolution);
NAPI_EXTERN napi_status napi_reject_deferred(napi_env env, napi_deferred deferred, napi_value rejection);
NAPI_EXTERN napi_status napi_is_promise(napi_env env, napi_value value, bool* is_promise);

// Running a script，执行脚本，猜测是evl
NAPI_EXTERN napi_status napi_run_script(napi_env env, napi_value script, napi_value* result);

// 内存管理
NAPI_EXTERN napi_status napi_adjust_external_memory(napi_env env, int64_t change_in_bytes, int64_t* adjusted_value);


// Dates
NAPI_EXTERN napi_status napi_create_date(napi_env env, double time, napi_value* result);
NAPI_EXTERN napi_status napi_is_date(napi_env env, napi_value value, bool* is_date);
NAPI_EXTERN napi_status napi_get_date_value(napi_env env, napi_value value, double* result);

// Add finalizer for pointer
NAPI_EXTERN napi_status napi_add_finalizer(napi_env env, napi_value js_object, void* native_object, napi_finalize finalize_cb, void* finalize_hint, napi_ref* result);

// BigInt 
NAPI_EXTERN napi_status napi_create_bigint_int64(napi_env env, int64_t value, napi_value* result);
NAPI_EXTERN napi_status napi_create_bigint_uint64(napi_env env, uint64_t value, napi_value* result);
NAPI_EXTERN napi_status napi_create_bigint_words(napi_env env, int sign_bit, size_t word_count, const uint64_t* words, napi_value* result);
NAPI_EXTERN napi_status napi_get_value_bigint_int64(napi_env env, napi_value value, int64_t* result, bool* lossless);
NAPI_EXTERN napi_status napi_get_value_bigint_uint64(napi_env env, napi_value value, uint64_t* result, bool* lossless);
NAPI_EXTERN napi_status napi_get_value_bigint_words(napi_env env, napi_value value, int* sign_bit, size_t* word_count, uint64_t* words);

// Object 
napi_get_all_property_names(napi_env env, napi_value object, napi_key_collection_mode key_mode, napi_key_filter key_filter, napi_key_conversion key_conversion, napi_value* result);

// Instance data
NAPI_EXTERN napi_status napi_set_instance_data(napi_env env, void* data, napi_finalize finalize_cb, void* finalize_hint);
NAPI_EXTERN napi_status napi_get_instance_data(napi_env env, void** data); 
// ArrayBuffer detaching
NAPI_EXTERN napi_status napi_detach_arraybuffer(napi_env env, napi_value arraybuffer);
NAPI_EXTERN napi_status napi_is_detached_arraybuffer(napi_env env, napi_value value, bool* result);  
// Type tagging，类型标签
NAPI_EXTERN napi_status napi_type_tag_object(napi_env env, napi_value value, const napi_type_tag* type_tag);
napi_check_object_type_tag(napi_env env, napi_value value, const napi_type_tag* type_tag, bool* result);
NAPI_EXTERN napi_status napi_object_freeze(napi_env env, napi_value object);
NAPI_EXTERN napi_status napi_object_seal(napi_env env, napi_value object);
```
:::  

## 具体细节  
### 获取函数的参数   
传入函数的参数被存放在`napi_callback_info` 中，可以通过`napi_get_cb_info` 函数来提取。需要注意的是，在自定义插件中定义的函数，参数数量一般来说最好与`JS` 约定好。  

```c{16-19}
/**
* // 一次调用获取所有回调函数的信息。(Ugly, but faster.)
* NAPI_EXTERN napi_status napi_get_cb_info(
*     napi_env env,               // [in] 运行环境
*     napi_callback_info cbinfo,  // [in] 回调函数的参数
*     size_t* argc,      // [in-out] 预设置取参数的数量
*                        // 返回实际取到的参数数量
*     napi_value* argv,  // [out] 参数数组
*     napi_value* this_arg,  // [out] 获取函数调用时this 对象
*     void** data);          // [out] 获取该函数的数据指针（不太懂
*/
static napi_value Add(napi_env env, napi_callback_info info) {
  napi_status status;

  // 1. 从napi_callback_info 提取参数及其数量
  size_t argc = 2;
  napi_value args[2];
  status = napi_get_cb_info(env, info, &argc, args, NULL, NULL);
  assert(status == napi_ok);

  if (argc < 2) {
    // 抛出异常
    napi_throw_type_error(env, NULL, "Wrong number of arguments");
    return NULL;
  }

  // 2. 获取参数类型
  napi_valuetype valuetype0;
  status = napi_typeof(env, args[0], &valuetype0);
  assert(status == napi_ok);

  napi_valuetype valuetype1;
  status = napi_typeof(env, args[1], &valuetype1);
  assert(status == napi_ok);

  // 3. 判断参数类型
  if (valuetype0 != napi_number || valuetype1 != napi_number) {
    napi_throw_type_error(env, NULL, "Wrong arguments");
    return NULL;
  }

  // 4. 获取数据值
  double value0;
  status = napi_get_value_double(env, args[0], &value0);
  assert(status == napi_ok);

  double value1;
  status = napi_get_value_double(env, args[1], &value1);
  assert(status == napi_ok);

  napi_value sum;
  status = napi_create_double(env, value0 + value1, &sum);
  assert(status == napi_ok);

  return sum;
  // 从上面的代码来看，获取函数参数的部分存在着大量的重复代码（对开发者而言），
  // 当然这些代码在程序执行时都是必须的，但是考虑到开发效率，我们依然需要能提取
  // 代码的冗余部分，进行封装。
}
```

### 调用（回调）函数  
主要用来调用传入的JS 回调函数。  
```c
/**
* NAPI_EXTERN napi_status napi_call_function(napi_env env,
*                                           napi_value recv,        // this 对象
*                             // 非实例函数可以用napi_get_global() 获取global 对象
*                                           napi_value func,           // 函数体
*                                           size_t argc,             // 参数数量 
*                                           const napi_value* argv,  // 传入参数
*                                           napi_value* result);       // 返回值
*/
static napi_value RunCallback(napi_env env, const napi_callback_info info) {
  napi_status status;

  size_t argc = 1;
  napi_value args[1];
  status = napi_get_cb_info(env, info, &argc, args, NULL, NULL);
  assert(status == napi_ok);

  napi_value cb = args[0];

  napi_value argv[1];
  status = napi_create_string_utf8(env, "hello world", NAPI_AUTO_LENGTH, argv);
  assert(status == napi_ok);

  napi_value global;
  status = napi_get_global(env, &global);
  assert(status == napi_ok);

  napi_value result;
  status = napi_call_function(env, global, cb, 1, argv, &result);
  assert(status == napi_ok);

  return NULL;
}

static napi_value Init(napi_env env, napi_value exports) {
  napi_value new_exports;
  napi_status status = napi_create_function(
      env, "", NAPI_AUTO_LENGTH, RunCallback, NULL, &new_exports);
  assert(status == napi_ok);
  // 其实导出的对象也是一个普通的napi_value
  return new_exports;
}
/**
* 创建函数
* napi_status napi_create_function(napi_env env,          //
*                                  const char* utf8name,  // 函数名，留空表示匿名函数？
*                                  size_t length,         // 函数名长度，或者NAPI_AUTO_LENGTH 
*                                  napi_callback cb,      // 函数体
*                                  void* data,            // 用户提供的数据上下文，调用时传递回函数。 
*                                  napi_value* result);   // 返回值：返回一个函数类型
*/
```

### 对象工厂  
创建JS 对象的方法。  
```c{20}
/**
* NAPI_EXTERN napi_status napi_set_named_property(napi_env env,  //
*                                          napi_value object,    // 
*                                          const char* utf8name, // 属性名
*                                          napi_value value);    // 属性值
*/

static napi_value CreateObject(napi_env env, const napi_callback_info info) {
  napi_status status;

  size_t argc = 1;
  napi_value args[1];
  status = napi_get_cb_info(env, info, &argc, args, NULL, NULL);
  assert(status == napi_ok);

  napi_value obj;
  status = napi_create_object(env, &obj);
  assert(status == napi_ok);

  status = napi_set_named_property(env, obj, "msg", args[0]);
  assert(status == napi_ok);

  return obj;
}

// 导出为匿名函数
static napi_value Init(napi_env env, napi_value exports) {
  napi_value new_exports;
  napi_status status = napi_create_function(
      env, "", NAPI_AUTO_LENGTH, CreateObject, NULL, &new_exports);
  assert(status == napi_ok);
  return new_exports;
}

NAPI_MODULE(NODE_GYP_MODULE_NAME, Init)
```

### 函数工厂  
函数工厂就是构建JS 函数的方法，前文已经提到过了。  
```c
// 返回"hello world"
static napi_value MyFunction(napi_env env, napi_callback_info info) {
  napi_status status;

  napi_value str;
  status = napi_create_string_utf8(env, "hello world", NAPI_AUTO_LENGTH, &str);
  assert(status == napi_ok);

  return str;
}

static napi_value CreateFunction(napi_env env, napi_callback_info info) {
  napi_status status;

  napi_value fn;
  status = napi_create_function(
      env, "theFunction", NAPI_AUTO_LENGTH, MyFunction, NULL, &fn);
  assert(status == napi_ok);

  return fn;
}
```

## 晋级C++  
前面我们基本上已经了解了`C` 语言插件的开发，特点就是代码很长。于是我们可以采用面向对象的方式来封装代码。于是，以后将开始引入`C++`，将JS 对象与CPP 对象一一对应起来。然鹅对于不熟悉`C++` 的我来说，看代码果然还是太难了些。  

### 对象的封装  
封装一个自定义的`C++` 对象类型，并将函数、属性、初始化的方法，统统写到对象内部。这样就可以只对外保留导出模块的接口了。似乎每一个模块都会有一个实例`instance`。**而`Constructor,New` 则应该是约定好的，会被JS 调用的函数名。**看一遍源码只能说能了解个大概，真要是用还需要大量的练习。  

<CodeGroup>
<CodeGroupItem title="addon.cc">

```c++{4}
#include "myobject.h"

napi_value Init(napi_env env, napi_value exports) {
  return MyObject::Init(env, exports);
}

NAPI_MODULE(NODE_GYP_MODULE_NAME, Init)
```

</CodeGroupItem>

<CodeGroupItem title="myobject.h">

```c++
#ifndef TEST_ADDONS_NAPI_6_OBJECT_WRAP_MYOBJECT_H_
#define TEST_ADDONS_NAPI_6_OBJECT_WRAP_MYOBJECT_H_

#include <node_api.h>

class MyObject {
 public:
  static napi_value Init(napi_env env, napi_value exports);
  static void Destructor(napi_env env, void* nativeObject, void* finalize_hint);

 private:
  // explicit 拒绝构造函数的隐式调用，总之能用就用
  explicit MyObject(double value_ = 0);
  ~MyObject();

  static napi_value New(napi_env env, napi_callback_info info);
  static napi_value GetValue(napi_env env, napi_callback_info info);
  static napi_value SetValue(napi_env env, napi_callback_info info);
  static napi_value PlusOne(napi_env env, napi_callback_info info);
  static napi_value Multiply(napi_env env, napi_callback_info info);
  static inline napi_value Constructor(napi_env env);

  double value_;
  napi_env env_;
  napi_ref wrapper_;
};

#endif  // TEST_ADDONS_NAPI_6_OBJECT_WRAP_MYOBJECT_H_
```

</CodeGroupItem>
<CodeGroupItem title="myobject.cc">

```c++
#include "myobject.h"
#include <assert.h>

// 多继承，对象派生自：value_(value), env_(nullptr), wrapper_(nullptr)
// 需要注意的是，对象本身的值存放于value_(value)
MyObject::MyObject(double value)
    : value_(value), env_(nullptr), wrapper_(nullptr) {}  

MyObject::~MyObject() {
  // 删除JS 引用
  napi_delete_reference(env_, wrapper_);
}

void MyObject::Destructor(napi_env env,
                          void* nativeObject,
                          void* /*finalize_hint*/) {
  
  // reinterpret_cast 运算符并不会改变括号中运算对象的值，而是对该对象从位模式上进行重新解释
  reinterpret_cast<MyObject*>(nativeObject)->~MyObject();
  // 调用析构函数
}

// 定义属性描述符
#define DECLARE_NAPI_METHOD(name, func)                                        \
  { name, 0, func, 0, 0, 0, napi_default, 0 }

// 用于初始化模块，并返回构造好的.node 模块
napi_value MyObject::Init(napi_env env, napi_value exports) {
  napi_status status;
  // 创建属性描述符
  napi_property_descriptor properties[] = {
      // 添加property->value，同时也包含getter,setter
      {"value", 0, 0, GetValue, SetValue, 0, napi_default, 0},
      // 对象包含两个方法
      DECLARE_NAPI_METHOD("plusOne", PlusOne),
      DECLARE_NAPI_METHOD("multiply", Multiply),
  };

  /**
  * 定义JS 类
  * napi_status napi_define_class(napi_env env,
  *                             const char* utf8name,      // 类名
  *                             size_t length,             // 类名长度
  *                             napi_callback constructor, // 构造函数
  *                             void* data,                // 传入构造函数的data（可选）
  *                             size_t property_count,     // 类属性长度
  *                             const napi_property_descriptor* properties,
  *                                                        // 类属性数组
  *                             napi_value* result);       // 返回类对象
  */
  napi_value cons;
  status = napi_define_class(
      env, "MyObject", NAPI_AUTO_LENGTH, New, nullptr, 3, properties, &cons);
  assert(status == napi_ok);

  // 因为插件的Init 之后，我们还需要调用此构造函数，所以
  // 我们需要创建一个强引用，将其持久化存储。这样我们就能
  // 在插件中任何位置，通过`napi_get_instance_data` 检
  // 索到它。我们不能将其设置为全局的静态变量，因为这样的
  // 话无法支持worker 线程以及单线程的多个上下文。
  napi_ref* constructor = new napi_ref;
  status = napi_create_reference(env, cons, 1, constructor);  // 创建强引用
  assert(status == napi_ok);
  status = napi_set_instance_data(  // 添加到实例
      env,          // 
      constructor,  // void* data。存入的数据
      // 卸载插件时会调用此lambda 函数，来释放强引用与堆内存
      [](napi_env env, void* data, void* hint) {
        napi_ref* constructor = static_cast<napi_ref*>(data);
        napi_status status = napi_delete_reference(env, *constructor);
        assert(status == napi_ok);
        delete constructor;
      },            // napi_finalize finalize_cb。卸载插件时的回调函数
      nullptr);     // 可选提示
  assert(status == napi_ok);

  status = napi_set_named_property(env, exports, "MyObject", cons);
  assert(status == napi_ok);
  return exports;
}

// 对应JS 中的构造函数
napi_value MyObject::Constructor(napi_env env) {
  // 获取存放在示例中的构造函数的引用
  void* instance_data = nullptr;
  napi_status status = napi_get_instance_data(env, &instance_data);
  assert(status == napi_ok);
  napi_ref* constructor = static_cast<napi_ref*>(instance_data);

  napi_value cons;
  status = napi_get_reference_value(env, *constructor, &cons);
  assert(status == napi_ok);
  return cons;
}

napi_value MyObject::New(napi_env env, napi_callback_info info) {
  napi_status status;

  napi_value target;
  status = napi_get_new_target(env, info, &target);  
  assert(status == napi_ok);
  bool is_constructor = target != nullptr;
  // new.target指向被new调用的构造函数，如果该方法不是构造函数，则会返回null

  if (is_constructor) {
    // 被当作构造函数调用
    // Invoked as constructor: `new MyObject(...)`
    size_t argc = 1;
    napi_value args[1];
    napi_value jsthis;  // 构造函数应有this
    status = napi_get_cb_info(env, info, &argc, args, &jsthis, nullptr);
    assert(status == napi_ok);

    double value = 0;

    napi_valuetype valuetype;
    status = napi_typeof(env, args[0], &valuetype);
    assert(status == napi_ok);

    if (valuetype != napi_undefined) {
      status = napi_get_value_double(env, args[0], &value);
      assert(status == napi_ok);
    }

    MyObject* obj = new MyObject(value);

    obj->env_ = env;
    status = napi_wrap(env,
                       jsthis,  // 将obj 包装成this
                       reinterpret_cast<void*>(obj),  // 本地对象
                       MyObject::Destructor,  // 准备垃圾回收时销毁本地对象
                       nullptr,  // finalize_hint，可选提示
                       &obj->wrapper_);  // 返回值
    assert(status == napi_ok);

    return jsthis;
  } else {
    // 被当作普通函数调用
    // Invoked as plain function `MyObject(...)`, turn into construct call.
    size_t argc_ = 1;
    napi_value args[1];
    status = napi_get_cb_info(env, info, &argc_, args, nullptr, nullptr);
    assert(status == napi_ok);

    const size_t argc = 1;
    napi_value argv[argc] = {args[0]};

    napi_value instance;
    status = napi_new_instance(env, Constructor(env), argc, argv, &instance);
    assert(status == napi_ok);

    return instance;
  }
}

// Getter、Setter
napi_value MyObject::GetValue(napi_env env, napi_callback_info info) {
  napi_status status;

  napi_value jsthis;
  status = napi_get_cb_info(env, info, nullptr, nullptr, &jsthis, nullptr);
  assert(status == napi_ok);

  MyObject* obj;
  // 解除包装
  status = napi_unwrap(env, jsthis, reinterpret_cast<void**>(&obj));
  assert(status == napi_ok);

  napi_value num;
  status = napi_create_double(env, obj->value_, &num);
  assert(status == napi_ok);

  return num;
}

napi_value MyObject::SetValue(napi_env env, napi_callback_info info) {
  napi_status status;

  size_t argc = 1;
  napi_value value;
  napi_value jsthis;
  status = napi_get_cb_info(env, info, &argc, &value, &jsthis, nullptr);
  assert(status == napi_ok);

  MyObject* obj;
  status = napi_unwrap(env, jsthis, reinterpret_cast<void**>(&obj));
  assert(status == napi_ok);

  // 虽然是get 函数，但是将传入的值get 到对象属性上面去了。。。
  status = napi_get_value_double(env, value, &obj->value_);
  assert(status == napi_ok);

  return nullptr;
}

napi_value MyObject::PlusOne(napi_env env, napi_callback_info info) {
  napi_status status;

  napi_value jsthis;
  status = napi_get_cb_info(env, info, nullptr, nullptr, &jsthis, nullptr);
  assert(status == napi_ok);

  MyObject* obj;
  status = napi_unwrap(env, jsthis, reinterpret_cast<void**>(&obj));
  assert(status == napi_ok);

  obj->value_ += 1;

  napi_value num;
  status = napi_create_double(env, obj->value_, &num);
  assert(status == napi_ok);

  return num;
}

napi_value MyObject::Multiply(napi_env env, napi_callback_info info) {
  napi_status status;

  size_t argc = 1;
  napi_value args[1];
  napi_value jsthis;
  status = napi_get_cb_info(env, info, &argc, args, &jsthis, nullptr);
  assert(status == napi_ok);

  napi_valuetype valuetype;
  status = napi_typeof(env, args[0], &valuetype);
  assert(status == napi_ok);

  double multiple = 1;
  if (valuetype != napi_undefined) {
    status = napi_get_value_double(env, args[0], &multiple);
    assert(status == napi_ok);
  }

  MyObject* obj;
  status = napi_unwrap(env, jsthis, reinterpret_cast<void**>(&obj));
  assert(status == napi_ok);

  const int kArgCount = 1;
  napi_value argv[kArgCount];
  status = napi_create_double(env, obj->value_ * multiple, argv);
  assert(status == napi_ok);

  napi_value instance;
  status = napi_new_instance(env, Constructor(env), kArgCount, argv, &instance);
  assert(status == napi_ok);

  return instance;
}
```

</CodeGroupItem>
</CodeGroup>  

### 工厂封装   
仍然以`MyObject` 为例，工厂的封装其实就相当于增加了一个调用对象构造函数的层。  

```c++{12-14,21-22}
#include <assert.h>
#include "myobject.h"

napi_value CreateObject(napi_env env, napi_callback_info info) {
  napi_status status;

  size_t argc = 1;
  napi_value args[1];
  status = napi_get_cb_info(env, info, &argc, args, nullptr, nullptr);
  assert(status == napi_ok);

  napi_value instance;
  status = MyObject::NewInstance(env, args[0], &instance);
  assert(status == napi_ok);

  return instance;
}

napi_value Init(napi_env env, napi_value exports) {
  // 仍然需要在加载插件时初始化MyObject 类
  napi_status status = MyObject::Init(env);
  assert(status == napi_ok);

  napi_value new_exports;
  status = napi_create_function(
      env, "", NAPI_AUTO_LENGTH, CreateObject, nullptr, &new_exports);
  assert(status == napi_ok);
  return new_exports;
}

NAPI_MODULE(NODE_GYP_MODULE_NAME, Init)
```

### Passing_Wraoed  
说实话这一节我不知道该如何翻译，因为内容开起来与前面的东西没有什么不同。无非是增加了一个函数，可以将JS 对象转化为C++ 对象并进行处理。  
```c++
#include <assert.h>
#include "myobject.h"

// 对象工厂
napi_value CreateObject(napi_env env, napi_callback_info info) {
  napi_status status;

  size_t argc = 1;
  napi_value args[1];
  status = napi_get_cb_info(env, info, &argc, args, nullptr, nullptr);
  assert(status == napi_ok);

  napi_value instance;
  status = MyObject::NewInstance(env, args[0], &instance);

  return instance;
}

// 对象的加法函数
napi_value Add(napi_env env, napi_callback_info info) {
  napi_status status;

  size_t argc = 2;
  napi_value args[2];
  status = napi_get_cb_info(env, info, &argc, args, nullptr, nullptr);
  assert(status == napi_ok);

  // 类型转换
  MyObject* obj1;
  status = napi_unwrap(env, args[0], reinterpret_cast<void**>(&obj1));
  assert(status == napi_ok);

  MyObject* obj2;
  status = napi_unwrap(env, args[1], reinterpret_cast<void**>(&obj2));
  assert(status == napi_ok);

  napi_value sum;
  status = napi_create_double(env, obj1->Val() + obj2->Val(), &sum);
  assert(status == napi_ok);

  return sum;
}

#define DECLARE_NAPI_METHOD(name, func)                                        \
  { name, 0, func, 0, 0, 0, napi_default, 0 }

napi_value Init(napi_env env, napi_value exports) {
  napi_status status;

  MyObject::Init(env);

  napi_property_descriptor desc[] = {
      DECLARE_NAPI_METHOD("createObject", CreateObject),
      DECLARE_NAPI_METHOD("add", Add),
  };
  status =
      napi_define_properties(env, exports, sizeof(desc) / sizeof(*desc), desc);
  assert(status == napi_ok);
  return exports;
}

NAPI_MODULE(NODE_GYP_MODULE_NAME, Init)
```

看到这里，我们就会发现，虽然可以使用C++ 来封装代码，但是工作量依然好大，能不能再简单一些，让我们可以直接写C++ 代码就行了。幸运的是，官方已经在维护这样的库了：[node-addon-api](https://github.com/nodejs/node-addon-api)。  

## node-addon-api   
在理解了上述代码之后，就理清了`n-api` 插件的工作原理，基于`node-addon-api` 的开发也就水到渠成了。下面仅记录一下`node-addon-api` 的安装过程。  
### 前提条件  
- 已经安装了NodeJS
- 已经安装了node-gyp  

### 安装和使用  
1. 在`package.json` 中添加依赖项：  
    ```json
    // yarn add node-addon-api
    "dependencies": {
      "node-addon-api": "*",
    }
    ```
2. 在`binding.gyp` 中添加头文件引用  
    ```json
    'include_dirs': ["<!(node -p \"require('node-addon-api').include_dir\")"],
    ```
3. 在`binding.gyp` 中声明是否启用`C++` 异常功能。因为基本的C-API 不会抛出或者处理C++ 异常，而C++ 包装器却可以选择启用[此功能](https://github.com/nodejs/node-addon-api/blob/HEAD/doc/error_handling.md)
    ```json
    'cflags!': [ '-fno-exceptions' ],
    'cflags_cc!': [ '-fno-exceptions' ],
    'xcode_settings': {
      'GCC_ENABLE_CPP_EXCEPTIONS': 'YES',
      'CLANG_CXX_LIBRARY': 'libc++',
      'MACOSX_DEPLOYMENT_TARGET': '10.7',
    },
    'msvs_settings': {
      'VCCLCompilerTool': { 'ExceptionHandling': 1 },
    },
    # 或者干脆禁用掉此功能  
    'defines': [ 'NAPI_DISABLE_CPP_EXCEPTIONS' ],
    ```
4. 配置支持`OSX`  
    ```json
    'conditions': [
      ['OS=="mac"', {
        'cflags+': ['-fvisibility=hidden'],
        'xcode_settings': {
          'GCC_SYMBOLS_PRIVATE_EXTERN': 'YES', # -fvisibility=hidden
        }
      }]
    ]
    ```
5. 在项目代码中引入头文件  
    ```c++
    #include "napi.h"
    ```
在构建时，只有当目标节点版本没有内置 Node-API 时，才会使用 Node-API back-compat 库代码。

预处理器指令`NODE_ADDON_API_DISABLE_DEPRECATED` 可以在编译时定义，然后包含 `napi.h` 以跳过不推荐使用的API 的定义。    
6. 导入插件，示例中采用`node-bindings` 库来导入编译好的文件。因为一般编译好的文件会存在于`./Release/*` 比较深层的目录，比较不好找。  

### 创建第一个项目  
一般我们采用框架来自动生成代码，这里用到了`Yoman` 和`generator-napi-module` 两个库  
```powershell  
npm install -g yo
npm install -g generator-napi-module

# 创建项目文件夹
mkdir hello-world
cd hello-world
yo napi-module

# 项目配置选项
package name: (hello-world) 
version: (1.0.0) 
description: A first project.
git repository: 
keywords: 
author: Your name goes here
license: (ISC)
Yeoman will display the generated package.json file here.


Is this OK? (yes) yes
? Choose a template Hello World
? Would you like to generate TypeScript wrappers for your module? No
```

## 相关资料  
1. [node-addon-examples](https://github.com/nodejs/node-addon-examples)  
2. [C/C++ addons with Node-API](https://nodejs.org/docs/latest/api/n-api.html)  
3. [node-addon-api](https://github.com/nodejs/node-addon-api)  
4. [Node-API Resource](https://nodejs.github.io/node-addon-examples/)  
5. [A first project](https://napi.inspiredware.com/getting-started/first.html)：主要介绍如何构建一个N-API 项目  
