%define major   0
%define libname %mklibname	open-vm-tools %major
%define devname %mklibname      open-vm-tools -d
%define	svn_rev 1098359
%define	Werror_cflags %nil

Name:           open-vm-tools
Group:          System/Emulators/PC
Summary:        Open Virtual Machine Tools
Version:        2013.04.16
Release:        2
Url:            http://open-vm-tools.sourceforge.net/
License:        BSD 3-Clause; GPL v2 only; LGPL v2.1 only
Source0:        %{name}-%{version}-%{svn_rev}.tar.gz
BuildRequires:	icu-devel
BuildRequires:	pcre-devel
BuildRequires:  gtk+2.0-devel
BuildRequires:  dnet-devel
BuildRequires:  gtkmm2.4-devel
BuildRequires:  pkgconfig(x11)
BuildRequires:  doxygen fuse-devel
BuildRequires:	pkgconfig(xtst)
BuildRequires:	pkgconfig(libprocps)
BuildRequires:	pkgconfig(gdk-pixbuf-xlib-2.0)

Requires:	%{libname} = %{version}-%{release}
Requires:	%{name}-plugins	

%description
Open Virtual Machine Tools (open-vm-tools) are the open source
implementation of VMware Tools. They are a set of guest operating
system virtualization components that enhance performance and user
experience of virtual machines. As virtualization technology rapidly
becomes mainstream, each virtualization solution provider implements
their own set of tools and utilities to supplement the guest virtual
machine. However, most of the implementations are proprietary and are
tied to a specific virtualization platform.

With the Open Virtual Machine Tools project, we are hoping to solve
this and other related problems. The tools are currently composed of
kernel modules for Linux and user-space programs for all VMware
supported Unix-like guest operating systems. They provide several
useful functions like:

* File transfer between a host and guest

* Improved memory management and network performance under
   virtualization

* General mechanisms and protocols for communication between host and
guests and from guest to guest

%package -n	%devname
Summary:	Open Virtual Machine Tools development files
License:	BSD 3-Clause; GPL v2 only; LGPL v2.1 only
Group:		System/Kernel and hardware	
Requires:       %{libname} = %{version}-%{release}
Provides:	open-vm-tools-devel = %{version}-%{release}


%description -n %devname
Open Virtual Machine Tools development files

%package -n	open-vm-tools-plugins
Summary:	Open Virtual Machine Tools plugins
License:	BSD 3-Clause; GPL v2 only; LGPL v2.1 only
Group:		System/Kernel and hardware
Requires:	%{libname} = %{version}-%{release}
Requires:	%{name} = %{version}-%{release}


%package -n	%libname
Summary:	Open Virtual Machine Tools libs
Group:		System/Libraries
Requires:	%{name} = %{version}-%{release}


%description -n	%libname
Open Virtual Machine Tools (open-vm-tools) are the open source
implementation of VMware Tools. They are a set of guest operating
system virtualization components that enhance performance and user
experience of virtual machines. As virtualization technology rapidly
becomes mainstream, each virtualization solution provider implements
their own set of tools and utilities to supplement the guest virtual
machine. However, most of the implementations are proprietary and are
tied to a specific virtualization platform.




%prep
%setup -q -n %{name}-%{version}-%{svn_rev}
#% patch0 -p1
chmod -x AUTHORS COPYING ChangeLog NEWS README

# Do not filter out Werror
# Upstream Bug  http://sourceforge.net/tracker/?func=detail&aid=2959749&group_id=204462&atid=989708
# sed -i -e 's/CFLAGS=.*Werror/#&/g' configure || die "sed comment out Werror failed"
sed -i -e 's:\(TEST_PLUGIN_INSTALLDIR=\).*:\1\$libdir/open-vm-tools/plugins/tests:g' configure
sed -i -e 's:\(TEST_PLUGIN_INSTALLDIR=\).*:\1\$libdir/open-vm-tools/plugins/tests:g' configure
sed -i -e 's/proc-3.2.7/proc-3.3.8/g' configure* 
sed -i -e 's/-Werror//g' configure.ac

%build
autoreconf -fiv
#export CUSTOM_PROCPS_NAME=procps
#export CUSTOM_PROCPS_LIBS="pkg-config --libs libprocps"
find ./ -name Makefile | xargs sed -i -e 's/-Werror//g'
%configure \
    --without-kernel-modules \
    --with-procps \
    --with-dnet \
    --disable-dependency-tracking

%make LIBS="-ltirpc" CFLAGS="%optflags -Wno-implicit-function-declaration"

%install
%makeinstall_std
find . -name \*.la -delete
#ln -s % {buildroot}/ % {_sbindir}/mount.vmhgfs % {buildroot}/sbin/mount.vmhgfs

rm -f %{buildroot}/sbin/mount.vmhgfs

ln -s ../%{_sbindir}/mount.vmhgfs %{buildroot}/sbin/mount.vmhgfs

rm -f %{buildroot}/%{_libdir}/{*.la,*.a}
rm -f %{buildroot}/%{_libdir}/%{name}/plugins/common/{*.la,*.a}

%files
%doc AUTHORS COPYING ChangeLog NEWS README
%{_bindir}/*
%{_sbindir}/mount.vmhgfs
/sbin/mount.vmhgfs
%config %{_sysconfdir}/vmware-tools
%config %{_sysconfdir}/pam.d/vmtoolsd
%{_datadir}/open-vm-tools/
%{_sysconfdir}/xdg/autostart/vmware-user.desktop

%files -n %libname
%{_libdir}/libguestlib.so.*
%{_libdir}/libhgfs.so.*
%{_libdir}/libvmtools.so.*

%files -n open-vm-tools-plugins
%{_libdir}/open-vm-tools/plugins/common/libhgfsServer.so
%{_libdir}/open-vm-tools/plugins/common/libvix.so
%{_libdir}/open-vm-tools/plugins/vmsvc/libguestInfo.so
%{_libdir}/open-vm-tools/plugins/vmsvc/libpowerOps.so
%{_libdir}/open-vm-tools/plugins/vmsvc/libtimeSync.so
%{_libdir}/open-vm-tools/plugins/vmsvc/libvmbackup.so
%{_libdir}/open-vm-tools/plugins/vmusr/libdesktopEvents.so
%{_libdir}/open-vm-tools/plugins/vmusr/libdndcp.so
%{_libdir}/open-vm-tools/plugins/vmusr/libresolutionSet.so

%files -n %devname 
%{_includedir}/vmGuestLib/*
%{_libdir}/libhgfs.so
%{_libdir}/pkgconfig/vmguestlib.pc
%{_libdir}/libguestlib.so
%{_libdir}/libvmtools.so
