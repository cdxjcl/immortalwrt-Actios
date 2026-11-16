# 修复 glib2-gobject 缺少 libffi.so.8 的构建失败

## 现象

GitHub Actions 在打包 `glib2-gobject` 时失败：

```text
Package glib2-gobject is missing dependencies for the following libraries:
libffi.so.8
```

## 根因

设备配置里曾显式关闭 libffi：

```text
# CONFIG_PACKAGE_libffi is not set
```

而 `glib2` / `glib2-gobject` / `glib2-gio` 都依赖 `libffi`。

早期锁定的 ImmortalWrt 基线中，`packages` feed 没有 libffi，所以当时在 CI 仓库里临时放了一份 3.4.7 的 `libffi` Makefile 做 overlay。

## 现在的情况

当前官方 ImmortalWrt 源码已经自带：

```text
package/libs/libffi/Makefile    libffi 3.8.0
package/libs/libffi/patches/    3.8.0 对应补丁
```

如果继续把旧的 3.4.7 Makefile 覆盖进去，就会变成：

```text
3.4.7 的 Makefile + 3.8.0 的 patches
```

于是 `003-powerpc64-fix-_Complex-long-double...` 等补丁全部失败。

## 最终修复

- 删除 CI 仓库里临时 vendored 的 `package/libs/libffi`；
- 使用官方源码自带的 libffi 3.8.0；
- 所有 `config/*.config` 保持：

```text
CONFIG_PACKAGE_libffi=y
```

这样 `libffi` 的版本和 patches 由同一次源码树提供，不会再出现版本混用。
