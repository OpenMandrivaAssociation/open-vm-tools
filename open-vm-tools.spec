%define devname %mklibname open-vm-tools -d
%define	svn_rev 1280544
%define	Werror_cflags %nil

Name:		open-vm-tools
Group:		Emulators
Summary:	Open Virtual Machine Tools
Version:	9.4.0
Epoch:		1
Release:	2
Url:		http://open-vm-tools.sourceforge.net/
License:	GPLv2
Source0:	%{name}-%{version}-%{svn_rev}.tar.gz
Source1:	vmtoolsd.service
Patch0:		g_info_redefine.patch
Patch1:		0001-fix-3.14-compatibility.patch
Patch2:		open-vm-tools-9.4.0-1280544-dkms.sh-destdir.patch
BuildRequires:	dnet-devel
BuildRequires:	doxygen
BuildRequires:	pkgconfig(fuse)
BuildRequires:	pkgconfig(gdk-pixbuf-xlib-2.0)
BuildRequires:  pkgconfig(gtk+-2.0)
BuildRequires:	pkgconfig(icu-uc)
BuildRequires:  pkgconfig(gtkmm-2.4)
BuildRequires:	pkgconfig(libpcre)
BuildRequires:  pkgconfig(x11)
BuildRequires:	pkgconfig(xtst)
BuildRequires:	pkgconfig(libprocps)

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

%package -n	%{devname}
Summary:	Open Virtual Machine Tools development files
Group:		System/Kernel and hardware	
Requires:       %{_lib}guestlib0 = %{EVRD}
Requires:       %{_lib}hgfs0 = %{EVRD}
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
%patch0 -p1 -b .g_info~
%patch1 -p1 -b .modules~
%patch2 -p1 -b .dkms_destdir~

# Remove "Encoding" key from the "Desktop Entry"
sed -e "s|^Encoding.*$||g" -i ./vmware-user-suid-wrapper/vmware-user.desktop.in


%build
export CUSTOM_PROCPS_NAME=procps
export CUSTOM_PROCPS_LIBS="$(pkg-config --libs libprocps)"
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
%{_libdir}/libhgfs.so
%{_libdir}/pkgconfig/vmguestlib.pc
%{_libdir}/libguestlib.so
%{_libdir}/libvmtools.so

%files -n dkms-%{name}
%{_usrsrc}/%{name}-%{version}-%{release}
