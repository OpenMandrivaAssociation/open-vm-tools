%define devname %mklibname open-vm-tools -d
%define	svn_rev 3227872
%define	Werror_cflags %nil

%define _disable_lto 1
%define _disable_ld_no_undefined 1

Name:		open-vm-tools
Group:		Emulators
Summary:	Open Virtual Machine Tools
Version:	10.0.5
Epoch:		1
Release:	1
Url:		http://open-vm-tools.sourceforge.net/
License:	GPLv2
Source0:	%{name}-%{version}-%{svn_rev}.tar.gz
Source1:	vmtoolsd.service
Patch0:		open-vm-tools-10.0.0-3000743-dkms.sh-destdir.patch
Patch1:		open-vm-tools-clang.patch
BuildRequires:	autoconf
BuildRequires:	dnet-devel
BuildRequires:	doxygen
BuildRequires:	pam-devel
BuildRequires:	pkgconfig(fuse)
BuildRequires:	pkgconfig(gdk-pixbuf-xlib-2.0)
BuildRequires:  pkgconfig(gtk+-2.0)
BuildRequires:	pkgconfig(icu-uc)
BuildRequires:  pkgconfig(gtkmm-2.4)
BuildRequires:	pkgconfig(libpcre)
BuildRequires:	pkgconfig(libtirpc)
BuildRequires:  pkgconfig(x11)
BuildRequires:	pkgconfig(xtst)
BuildRequires:	pkgconfig(libprocps)
BuildRequires:	pkgconfig(xerces-c)
BuildRequires:	pkgconfig(libmspack)
BuildRequires:	xml-security-c-devel

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

%{libpackage guestlib 0}
%{libpackage hgfs 0}
%{libpackage vmtools 0}
%{libpackage DeployPkg 0}
%{libpackage vgauth 0}

%package -n	%{devname}
Summary:	Open Virtual Machine Tools development files
Group:		System/Kernel and hardware	
Requires:	%{_lib}DeployPkg0 = %{EVRD}
Requires:       %{_lib}guestlib0 = %{EVRD}
Requires:       %{_lib}hgfs0 = %{EVRD}
Requires:	%{_lib}vgauth0 = %{EVRD}
Requires:       %{_lib}vmtools0 = %{EVRD}
Provides:	%{name}-devel = %{EVRD}

%description -n %{devname}
Open Virtual Machine Tools development files

%package	desktop
Summary:	User experience components for Open Virtual Machine Tools
Group:		System/Libraries
Requires:	%{name} = %{EVRD}

%description	desktop
This package contains only the user-space programs and libraries of
%{name} that are essential for improved user experience of VMware virtual
machines.

%package -n     dkms-%{name}
Summary:        Kernel modules for open-vm-tools
Group:          System/Kernel and hardware
License:        LGPLv2
Requires(post):	dkms
Requires(preun):dkms

%description -n dkms-%{name}
Kernel modules for open-vm-tools

%prep
%setup -q -n %{name}-%{version}-%{svn_rev}
%autopatch -p1

# Remove "Encoding" key from the "Desktop Entry"
sed -e "s|^Encoding.*$||g" -i vmware-user-suid-wrapper/vmware-user.desktop.in


%build
export CUSTOM_PROCPS_NAME=procps
export CUSTOM_PROCPS_LIBS="$(pkg-config --libs libprocps)"
export CFLAGS="%{optflags} -Wno-error -Dlinux=1"
export CXXFLAGS="%{optflags} -Wno-error -Dlinux=1"

autoreconf -fiv
export ac_cv_prog_ac_ct_have_cxx=%{__cxx}
export CXX='%{__cxx} -std=c++11'
%configure	--without-kernel-modules \
		--without-root-privileges \
		--with-procps \
		--with-dnet \
		LIBS="-ltirpc"

%make CFLAGS="%{optflags} -Wno-implicit-function-declaration"

%install
%makeinstall_std

chmod 644 %{buildroot}%{_sysconfdir}/pam.d/*
ln -sf %{_sbindir}/mount.vmhgfs %{buildroot}/sbin/mount.vmhgfs

# Move vm-support to /usr/bin
mv %{buildroot}%{_sysconfdir}/vmware-tools/vm-support %{buildroot}%{_bindir}

# Systemd unit files
install -p -m644 %{SOURCE1} -D %{buildroot}%{_unitdir}/vmtoolsd.service

##
## Package dkms
##
# Create dkms tree and fill it
sh modules/linux/dkms.sh . %{buildroot}%{_usrsrc}/%{name}-%{version}-%{release}

%post -n dkms-%{name}
/usr/sbin/dkms --rpm_safe_upgrade add -m %{name} -v %{version}-%{release}
/usr/sbin/dkms --rpm_safe_upgrade build -m %{name} -v %{version}-%{release}
/usr/sbin/dkms --rpm_safe_upgrade install -m %{name} -v %{version}-%{release}
:

%preun -n dkms-%{name}
set -x
/usr/sbin/dkms --rpm_safe_upgrade remove -m %{name} -v %{version}-%{release} --all
:

%files
%doc AUTHORS COPYING ChangeLog NEWS README
%config(noreplace) %{_sysconfdir}/pam.d/*
%{_sysconfdir}/vmware-tools/
%{_bindir}/vmtoolsd
%{_bindir}/vmware-checkvm
%{_bindir}/vmware-hgfsclient
%{_bindir}/vmware-rpctool
%{_bindir}/vmware-toolbox-cmd
%{_bindir}/vmware-xferlogs
%{_bindir}/vm-support
%{_bindir}/VGAuthService
%{_bindir}/vmhgfs-fuse
%{_bindir}/vmware-guestproxycerttool
%{_bindir}/vmware-vgauth-cmd
%{_sbindir}/mount.vmhgfs
/sbin/mount.vmhgfs
%dir %{_libdir}/%{name}/
%dir %{_libdir}/%{name}/plugins
%dir %{_libdir}/%{name}/plugins/common
%{_libdir}/%{name}/plugins/common/*.so
%dir %{_libdir}/%{name}/plugins/vmsvc
%{_libdir}/%{name}/plugins/vmsvc/*.so
%{_datadir}/%{name}/
%{_unitdir}/vmtoolsd.service

%files desktop
%{_sysconfdir}/xdg/autostart/*.desktop
%{_bindir}/vmware-user-suid-wrapper
%{_bindir}/vmware-vmblock-fuse
%{_libdir}/%{name}/plugins/vmusr/

%files -n %{devname}
%doc docs/api/build/*
%{_includedir}/vmGuestLib/*
%{_includedir}/libDeployPkg
%{_libdir}/libhgfs.so
%{_libdir}/pkgconfig/vmguestlib.pc
%{_libdir}/pkgconfig/libDeployPkg.pc
%{_libdir}/libguestlib.so
%{_libdir}/libvmtools.so
%{_libdir}/libDeployPkg.so
%{_libdir}/libvgauth.so

%files -n dkms-%{name}
%{_usrsrc}/%{name}-%{version}-%{release}
