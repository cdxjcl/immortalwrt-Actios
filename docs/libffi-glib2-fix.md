# 修复 glib2-gobject 缺少 libffi.so.8 的构建失败

## 现象

GitHub Actions 在打包 `glib2-gobject` 时失败：

```text
Package glib2-gobject is missing dependencies for the following libraries:
libffi.so.8
```

随后 `package/feeds/packages/glib2/compile` 失败，`make world` 退出码 2。后面的
“firmware file not found” 只是没有产物导致的连带错误。

## 根因

1. 设备配置里显式写了：

   ```text
   # CONFIG_PACKAGE_libffi is not set
   ```

   但 `glib2` / `glib2-gobject` / `glib2-gio` 都依赖 `libffi`，于是
   `glib2-gobject` 安装时检出 `libffi.so.8` 却没有对应包依赖。

2. 当前锁定的 ImmortalWrt snapshot 使用的
   `https://github.com/immortalwrt/packages.git` **master 分支已经没有
   `libs/libffi`**，所以即使只把配置改成 `=y`，feed 里也找不到这个包：

   ```text
   WARNING: No feed for package 'libffi' found
   ```

## 修复

1. 在仓库内自带一份 `libffi` 包（来自 `immortalwrt/packages` 的
   `openwrt-24.10` 分支，版本 3.4.7，ABI 为 `libffi.so.8`）：

   ```text
   package/libs/libffi/Makefile
   ```

2. workflow 在 `make defconfig` / `feeds install` 之前，把本地 `package/`
   叠加到上游源码树：

   ```text
   cp -a package/. openwrt/package/
   ```

3. 所有 `config/*.config` 把：

   ```text
   # CONFIG_PACKAGE_libffi is not set
   ```

   改为：

   ```text
   CONFIG_PACKAGE_libffi=y
   ```

## 为什么不用改 feed 分支

`packages` feed 如果用 `openwrt-24.10` 分支，会把整套 24.10 的包混进当前
snapshot，容易引入 ABI/依赖不匹配。只把 `libffi` 这一个独立库做成源码树内的
本地包，风险最小，也不影响其他包。

## 验证点

构建日志中应不再出现：

```text
Package glib2-gobject is missing dependencies for the following libraries:
libffi.so.8
```

同时应能看到 `libffi` 被编译并出现在 `glib2-gobject` 的依赖中。
