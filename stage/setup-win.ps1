$ErrorActionPreference = "Stop"

$CYG_ROOT = 'C:\cygwin'
$CYG_MIRROR = 'http://cygwin.mirror.constant.com'
$CYG_CACHE = 'C:\cygwin\var\cache\setup'
$CYG_BASH = 'C:\cygwin\bin\bash.exe'

if ( -Not ( Test-Path $CYG_BASH )) {
	$STARTDIR = $(get-location)
	cd ([System.IO.Path]::GetTempPath())
	Invoke-WebRequest "http://cygwin.com/setup-x86.exe" -OutFile "setup-x86.exe"
	.\setup-x86.exe --quiet-mode --no-shortcuts --only-site --root $CYG_ROOT --site $CYG_MIRROR --local-package-dir $CYG_CACHE --packages 'autoconf,automake,bison,gcc-core,gcc-g++,mingw-runtime,mingw-binutils,mingw-gcc-core,mingw-gcc-g++,mingw-pthreads,mingw-w32api,libtool,make,python,gettext-devel,gettext,intltool,libiconv,pkg-config,git,curl,wget'
	cygcheck -dc cygwin | Write-Output
	cd $STARTDIR
}
