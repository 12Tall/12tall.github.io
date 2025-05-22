; ModuleID = 'main.c'
source_filename = "main.c"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.32.31329"

$"??_C@_0BC@KNGDOBOK@?p?$JP?$KG?$JC?5hello?5?$CFs?$CB?5?6?$AA?$AA@" = comdat any

$"??_C@_06PMCOLED@world?$AA?$AA@" = comdat any

@"??_C@_0BC@KNGDOBOK@?p?$JP?$KG?$JC?5hello?5?$CFs?$CB?5?6?$AA?$AA@" = linkonce_odr dso_local unnamed_addr constant [18 x i8] c"\F0\9F\A6\92 hello %s! \0A\00\00", comdat, align 1
@fstr = dso_local global ptr @"??_C@_0BC@KNGDOBOK@?p?$JP?$KG?$JC?5hello?5?$CFs?$CB?5?6?$AA?$AA@", align 8
@"??_C@_06PMCOLED@world?$AA?$AA@" = linkonce_odr dso_local unnamed_addr constant [7 x i8] c"world\00\00", comdat, align 1

; Function Attrs: noinline nounwind optnone uwtable
define dso_local i32 @main() #0 {
  %1 = alloca i32, align 4
  %2 = alloca ptr, align 8
  store i32 0, ptr %1, align 4
  store ptr @"??_C@_06PMCOLED@world?$AA?$AA@", ptr %2, align 8
  ret i32 0
}

attributes #0 = { noinline nounwind optnone uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.module.flags = !{!0, !1, !2}
!llvm.ident = !{!3}

!0 = !{i32 1, !"wchar_size", i32 2}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"uwtable", i32 2}
!3 = !{!"clang version 16.0.0"}
