%define		major 0
%define		libdeploypkg %mklibname deploypkg %{major}
%define		libguestlib %mklibname guestlib %{major}
%define		libhgfs %mklibname hgfs %{major}
%define		libvgauth %mklibname vgauth %{major}
%define		libvmtools %mklibname vmtools %{major}
%define		devname %mklibname %{name} -d

Summary:		Open Virtual Machine Tools
Name:		open-vm-tools
Version:		12.5.2
Release:		1
License:		LGPLv2.1+
Group:		Emulators
Url:		https://github.com/vmware/open-vm-tools
Source0:	https://github.com/vmware/open-vm-tools/archive/refs/tags/stable-%{version}.tar.gz?/%{name}-stable-%{version}.tar.gz
# See, eg: https://bugzilla.redhat.com/show_bug.cgi?id=957135
Source1:	vmtoolsd.service
Source2:	vgauthd.service
Source3:	80-%{name}.preset
# See: https://kb.vmware.com/s/article/74650
Source4:	mnt-hgfs.mount
Source5:	%{name}.conf
Source6:	app-vmware-user.service
Source100:	%{name}.rpmlintrc
# See: https://github.com/vmware/open-vm-tools/issues/568
# https://github.com/vmware/open-vm-tools/pull/670
Patch0:		open-vm-tools-12.5.0-fix-vmuser-desktop-file.patch
# Errors from TimeInfoDataArray_* functions
Patch1:		open-vm-tools-12.5.0-workaround-unused-fuctions-errors.patch
BuildRequires:		doxygen
BuildRequires:		protobuf-compiler
BuildRequires:		dnet-devel
#BuildRequires:		golang-github-gogo-protobuf-devel
BuildRequires:		libtool-devel
BuildRequires:		pam-devel
BuildRequires:		pkgconfig(fuse3) >= 3.10.0
BuildRequires:		pkgconfig(gdk-pixbuf-2.0) >= 2.21
BuildRequires:		pkgconfig(glib-2.0) >= 2.34.0
BuildRequires:		pkgconfig(grpc++)
BuildRequires:		pkgconfig(gtk+-3.0)
BuildRequires:		pkgconfig(gtkmm-3.0)
BuildRequires:		pkgconfig(ice)
BuildRequires:		pkgconfig(icu-i18n)
BuildRequires:		pkgconfig(libcurl)
BuildRequires:		pkgconfig(libdrm)
BuildRequires:		pkgconfig(libmspack)
BuildRequires:		pkgconfig(libpcre)
BuildRequires:		pkgconfig(libproc2)
BuildRequires:		pkgconfig(libtirpc)
BuildRequires:		pkgconfig(libunwind)
BuildRequires:		pkgconfig(libxml-2.0)
BuildRequires:		pkgconfig(openssl)
BuildRequires:		pkgconfig(protobuf)
BuildRequires:		pkgconfig(sm)
BuildRequires:		pkgconfig(udev)
BuildRequires:		pkgconfig(x11)
BuildRequires:		pkgconfig(xcomposite)
BuildRequires:		pkgconfig(xext)
BuildRequires:		pkgconfig(xi)
BuildRequires:		pkgconfig(xinerama)
BuildRequires:		pkgconfig(xmlsec1)
BuildRequires:		pkgconfig(xrandr)
BuildRequires:		pkgconfig(xrender)
BuildRequires:		pkgconfig(xtst)
#Requires:	systemd-units
Requires(post,preun,postun):		systemd

%description
Open Virtual Machine Tools (aka %{name}) are the open source
implementation of VMware Tools, a set of guest operating system virtualization
components that enhance performance and user experience of virtual machines.
As virtualization technology rapidly becomes mainstream, each virtualization
solution provider implements their own set of tools and utilities to
supplement the guest virtual machine. However, most of the implementations are
proprietary and are tied to a specific virtualization platform. With the Open
Virtual Machine Tools project, we are hoping to solve this and other related
problems.
The tools are currently composed of kernel modules for Linux and user-space
programs for all VMware supported Unix-like guest operating systems. They
provide several useful functions like:
* File transfer between a host and guest.
* Improved memory management and network performance under virtualization.
* General mechanisms and protocols for communication between host and guests
 and from guest to guest.

%files
%doc AUTHORS COPYING ChangeLog NEWS ../ReleaseNotes.md ../README.md
%config(noreplace) %{_sysconfdir}/pam.d/*
%{_sysconfdir}/modules-load.d/%{name}.conf
%{_sysconfdir}/vmware-tools/
%{_unitdir}/vmtoolsd.service
%{_unitdir}/vgauthd.service
%{_unitdir}/app-vmware-user.service
%{_unitdir}/mnt-hgfs.mount
%{_sysconfdir}/systemd/80-%{name}.preset
%{_udevrulesdir}/99-vmware-scsi-udev.rules
%{_bindir}/VGAuthService
%{_bindir}/vm-support
%{_bindir}/vmhgfs-fuse
%{_bindir}/vmtoolsd
%{_bindir}/vmware-alias-import
%{_bindir}/vmware-checkvm
%{_bindir}/vmware-hgfsclient
%{_bindir}/vmware-namespace-cmd
%{_bindir}/vmware-rpctool
%{_bindir}/vmware-toolbox-cmd
%{_bindir}/vmware-user
%{_bindir}/vmware-user-suid-wrapper
%{_bindir}/vmware-vgauth-cmd
%{_bindir}/vmware-vgauth-smoketest
%{_bindir}/vmware-xferlogs
%{_bindir}/vmwgfxctrl
%dir %{_libdir}/%{name}/
%dir %{_libdir}/%{name}/plugins
%dir %{_libdir}/%{name}/plugins/common
%dir %{_libdir}/%{name}/plugins/vmsvc
%{_libdir}/%{name}/plugins/common/*.so
%{_libdir}/%{name}/plugins/vmsvc/*.so
%{_datadir}/%{name}/


%post
# Enable all services
%systemd_post vgauthd.service
%systemd_post vmtoolsd.service
%systemd_post app-vmware-user.service

%preun
%systemd_preun vmtoolsd.service
%systemd_preun vgauthd.service
%systemd_post app-vmware-user.service

# Tell VMware that open-vm-tools is being uninstalled
if [ "$1" = "0" ] && [ -x %{_bindir}/vmware-checkvm ] && [ -x %{_bindir}/vmware-rpctool ] && \
	%{_bindir}/vmware-checkvm 2>/dev/null &>/dev/null; then
		%{_bindir}/vmware-rpctool 'tools.set.version 0' 2>/dev/null &>/dev/null || /bin/true

# Teardown mount point for Shared Folders
		if [ -d /mnt/hgfs ] && %{_bindir}/vmware-checkvm -p | grep -q Workstation; then
		umount /mnt/hgfs &>/dev/null || /bin/true
		rmdir /mnt/hgfs &>/dev/null || /bin/true
		fi
fi

%postun
# ATM those macros do nothing
#systemd_user_postun vmtoolsd.service
#systemd_user_postun vgauthd.service
#systemd_user_postun app-vmware-user.service

# Cleanup GuestProxy certs
if [ "$1" = "0" ]; then
	rm -rf %{_sysconfdir}/vmware-tools/GuestProxyData &> /dev/null || /bin/true
fi

#----------------------------------------------------------------------------

%package -n %{libdeploypkg}
Summary:	Shared library for %{name}
Group:		System/Libraries

%description -n %{libdeploypkg}
Shared library for %{name}.

%files -n %{libdeploypkg}
%doc COPYING
%{_libdir}/libDeployPkg.so.%{major}*

#----------------------------------------------------------------------------

%package -n %{libguestlib}
Summary:	Shared library for %{name}
Group:		System/Libraries

%description -n %{libguestlib}
Shared library for %{name}.

%files -n %{libguestlib}
%doc COPYING
%{_libdir}/libguestlib.so.%{major}*
%{_libdir}/libguestStoreClient.so.%{major}*

#----------------------------------------------------------------------------

%package -n %{libhgfs}
Summary:	Shared library for %{name}
Group:		System/Libraries

%description -n %{libhgfs}
Shared library for %{name}.

%files -n %{libhgfs}
%doc COPYING
%{_libdir}/libhgfs.so.%{major}*

#----------------------------------------------------------------------------

%package -n %{libvgauth}
Summary:	Shared library for %{name}
Group:		System/Libraries

%description -n %{libvgauth}
Shared library for %{name}.

%files -n %{libvgauth}
%doc COPYING
%{_libdir}/libvgauth.so.%{major}*

#----------------------------------------------------------------------------

%package -n %{libvmtools}
Summary:	Shared library for %{name}
Group:		System/Libraries

%description -n %{libvmtools}
Shared library for %{name}.

%files -n %{libvmtools}
%doc COPYING
%{_libdir}/libvmtools.so.%{major}*

#----------------------------------------------------------------------------

%package -n %{devname}
Summary:	Open Virtual Machine Tools development files
Group:		Development/Other
Requires:	%{libdeploypkg} = %{EVRD}
Requires:	%{libguestlib} = %{EVRD}
Requires:	%{libhgfs} = %{EVRD}
Requires:	%{libvgauth} = %{EVRD}
Requires:	%{libvmtools} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}
Conflicts:	%{name}-devel < %{EVRD}

%description -n %{devname}
Open Virtual Machine Tools development files.

%files -n %{devname}
%doc docs/api/build/*
%{_defaultdocdir}/%{name}/api/html
%{_includedir}/libDeployPkg/*
%{_includedir}/vmGuestLib/*
%{_libdir}/libDeployPkg.so
%{_libdir}/libhgfs.so
%{_libdir}/libguestlib.so
%{_libdir}/libguestStoreClient.so
%{_libdir}/libvgauth.so
%{_libdir}/libvmtools.so
%{_libdir}/pkgconfig/libDeployPkg.pc
%{_libdir}/pkgconfig/vmguestlib.pc

#----------------------------------------------------------------------------

%package desktop
Summary:	User experience components for Open Virtual Machine Tools
Group:		Emulators
Requires:	%{name} = %{EVRD}

%description desktop
This package contains only the user-space programs of %{name} that are
essential for improved user experience of VMware virtual machines.

%files desktop
%doc COPYING
%{_sysconfdir}/xdg/autostart/*.desktop
%{_bindir}/vmware-vmblock-fuse
%{_libdir}/%{name}/plugins/vmusr/

#----------------------------------------------------------------------------

%prep
%autosetup -n %{name}-stable-%{version}/%{name} -p2

%build
%configure \
	--disable-static \
	--without-kernel-modules \
	--without-root-privileges \
	--disable-tests \
	--disable-containerinfo \
	--enable-vmwgfxctrl \
	--with-udev-rules-dir=%{_udevrulesdir} \
	--with-dnet \
	--with-fuse=3 \
	--with-gtk3 \
	--without-gtk2

sed -i -e 's! -shared ! -Wl,--as-needed\0!g' libtool

%make_build


%install
%make_install

# Install our systemd unit files
install -p -m644 %{SOURCE1} -D %{buildroot}%{_unitdir}/vmtoolsd.service
install -p -m644 %{SOURCE2} -D %{buildroot}%{_unitdir}/vgauthd.service
install -p -m644 %{SOURCE4} -D %{buildroot}%{_unitdir}/mnt-hgfs.mount
install -p -m644 %{SOURCE6} -D %{buildroot}%{_unitdir}/app-vmware-user.service
install -p -m644 %{SOURCE3} -D %{buildroot}%{_sysconfdir}/systemd/80-%{name}.preset
install -p -m644 %{SOURCE5} -D %{buildroot}%{_sysconfdir}/modules-load.d/%{name}.conf

# Fix perms
chmod 0644 %{buildroot}%{_sysconfdir}/pam.d/*
chmod 0644 %{buildroot}%{_sysconfdir}/vmware-tools/vgauth/schemas/*
