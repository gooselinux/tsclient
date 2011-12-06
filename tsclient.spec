
%define gtk2_version 2.2.0
%define gnome_panel 2.2.0
%define rdesktop_version 1.3.0
%define vnc_version 4.0
%define desktop_file_utils_version 0.4

Summary: Client for VNC and Windows Terminal Server
Name: tsclient
Version: 2.0.2
Release: 6%{?dist}
URL: http://sourceforge.net/projects/tsclient
Source0: http://downloads.sourceforge.net/%{name}/%{name}-%{version}.tar.bz2

License: GPL+
Group: User Interface/X
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires: rdesktop >= %{rdesktop_version}
Requires: vnc >= %{vnc_version}

BuildRequires: gnome-desktop-devel
BuildRequires: libgnomeui-devel
BuildRequires: libnotify-devel
BuildRequires: NetworkManager-glib-devel
BuildRequires: gtk2-devel >= %{gtk2_version}
BuildRequires: gnome-panel-devel >= %{gnome_panel}
BuildRequires: desktop-file-utils >= %{desktop_file_utils_version}
BuildRequires: gettext
BuildRequires: autoconf, automake, libtool, intltool

# reported upstream
Patch0: icon-names.patch
# reported upstream
Patch2: edit-dialog-crash.patch
# reported upstream
Patch3: vnc-password-optional.patch
# reported upstream
Patch4: vnc-remote-screen-size.patch
# NOT reported upstream; there's no simple way to make it support both
# realvnc and tightvnc
Patch5: realvnc-args.patch
Patch6: tsclient-libgnomeui.patch
Patch7: tsclient-glade-ids.patch

%description
tsclient is a frontend that makes it easy to use rdesktop and vncviewer.

%package devel
Summary: Header files needed to write tsclient plugins
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description devel
The tsclient-devel package contains header files that are needed to
develop tsclient plugins.

%prep
%setup -q
%patch0 -p1 -b .icon-names
%patch2 -p1 -b .edit-dialog-crash
%patch3 -p1 -b .vnc-password
%patch4 -p1 -b .vnc-remotesize
%patch5 -p1 -b .realvnc-args
%patch6 -p1 -b .libgnomeui
%patch7 -p1 -b .glade-ids
libtoolize --force --copy
autoreconf

%build

%configure

# drop unneeded direct library deps with --as-needed
# libtool doesn't make this easy, so we do it the hard way
sed -i -e 's/ -shared / -Wl,-O1,--as-needed\0 /g' -e 's/    if test "$export_dynamic" = yes && test -n "$export_dynamic_flag_spec"; then/      func_append compile_command " -Wl,-O1,--as-needed"\n      func_append finalize_command " -Wl,-O1,--as-needed"\n\0/' libtool

make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT

make install DESTDIR=$RPM_BUILD_ROOT

rm -rf $RPM_BUILD_ROOT/var/scrollkeeper

desktop-file-install --vendor tsclient --delete-original      \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications               \
  --remove-category Application                               \
  $RPM_BUILD_ROOT%{_datadir}/applications/*

rm -rf $RPM_BUILD_ROOT%{_libdir}/tsclient/plugins/*.{a,la}

%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule %{_sysconfdir}/gconf/schemas/tsc-handlers.schemas >& /dev/null || :
touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  gtk-update-icon-cache -q %{_datadir}/icons/hicolor
fi

%pre
if [ "$1" -gt 1 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/tsc-handlers.schemas >& /dev/null || :
fi

%preun
if [ "$1" -eq 0 ]; then
  export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
  gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/tsc-handlers.schemas >& /dev/null || :
fi

%postun
touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  gtk-update-icon-cache -q %{_datadir}/icons/hicolor
fi


%files -f %{name}.lang
%defattr(-,root,root)
%doc COPYING AUTHORS
%{_bindir}/*
%{_datadir}/applications/*.desktop
%{_sysconfdir}/gconf/schemas/tsc-handlers.schemas
%{_libdir}/tsclient
%{_datadir}/gnome/autostart/tsc-autostart.desktop
%{_datadir}/icons/hicolor/scalable/apps/tsclient.svg
%{_datadir}/tsclient

%files devel
%{_includedir}/tsclient


%changelog
* Thu Dec  3 2009 Matthias Clasen <mclasen@redhat.com> - 2.0.2-6
- Don't ship .la files

* Sat Aug 29 2009 Caolán McNamara <caolanm@redhat.com> - 2.0.2-5
- Rebuild for dependencies

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Jun 12 2009 Matthias Clasen <mclasen@redhat.com> - 2.0.2-3
- Fix some wrong ids in the glade file to make the ui work (#485976)
- Drop unneeded direct deps

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Jan 23 2009 Matthias Clasen <mclasen@redhat.com> - 2.0.2-1
- Update to 2.0.2

* Fri Jan 23 2009 Matthias Clasen <mclasen@redhat.com> - 2.0.1-11
- Don't add Utility to the desktop file categories

* Sat Dec 20 2008 Caolán McNamara <caolanm@redhat.com> - 2.0.1-10
- Rebuild

* Thu Nov 13 2008 Matthias Clasen <mclasen@redhat.com> - 2.0.1-9
- Rebuild

* Mon Oct 20 2008 Dan Winship <dwinship@redhat.com> - 2.0.1-2
- Fix crash when building without optimization on x86_64
- Allow VNC connections with no password (#460708)
- Allow VNC connections to use remote screen size as window size (#460709)
- Fix VNC code to work with RealVNC's vncviewer rather than TightVNC's

* Mon Aug 11 2008 Matthias Clasen <mclasen@redhat.com> - 2.0.1-1
- Update to 2.0.1

* Sun May  4 2008 Matthias Clasen <mclasen@redhat.com> - 0.150-7
- Fix source url

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.150-6
- Autorebuild for GCC 4.3

* Tue Oct 16 2007 Matthias Clasen <mclasen@redhat.com> - 0.150.5
- Don't crash when saving a connection  (#333461)

* Tue Oct  2 2007 Matthias Clasen <mclasen@redhat.com> - 0.150.4
- Require vnc, too (#158658)
- Fix license field

* Tue Aug 28 2007 Fedora Release Engineering <rel-eng at fedoraproject dot org> - 0.150-3
- Rebuild for selinux ppc32 issue.

* Sat Jul  7 2007 Matthias Clasen <mclasen@redhat.com> - 0.150-2
- Fix a directory ownership issue

* Fri Jun 15 2007 Matthias Clasen <mclasen@redhat.com> - 0.150-1
- Update to 0.150
- Readd the applet

* Sun Oct 29 2006 Matthias Clasen <mclasen@redhat.com> - 0.148-6
- Add the Utility category to make the menuitem show up (#212891)

* Tue Oct 17 2006 Matthias Clasen <mclasen@redhat.com> - 0.148-5
- Make the close button in the about dialog work (#203857)

* Sun Oct 01 2006 Jesse Keating <jkeating@redhat.com> - 0.148-4
- rebuilt for unwind info generation, broken in gcc-4.1.1-21

* Wed Sep 20 2006 Matthias Clasen <mclasen@redhat.com> - 0.148-3
- Don't include the applet, since it does not work (#206776)

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 0.148-2.1
- rebuild

* Sat Jun 10 2006 Matthias Clasen <mclasen@redhat.com> - 0.148-2
- Add missing BuildRequires

* Tue Jun  6 2006 Matthias Clasen <mclasen@redhat.com> - 0.148-1
- Update to 0.148

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 0.140-1.2.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 0.140-1.2
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Sun Oct  2 2005 Matthias Clasen <mclasen@redhat.com> 0.140-1
- Update to newer upstream version
- Fix a segfault (#169694)

* Mon Apr 25 2005 Matthias Clasen <mclasen@redhat.com> 0.132-6
- Make the icon appear in the "Add to Panel" dialog

* Wed Mar  2 2005 Mark McLoughlin <markmc@redhat.com> 0.132-5
- Rebuild with gcc4

* Tue Aug 17 2004 Florian La Roche <Florian.LaRoche@redhat.de>
- fix require lines

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Feb 19 2004 Mark McLoughlin <markmc@redhat.com> 0.132-2
- Add to the menus - bug #99570

* Wed Feb 18 2004 Mark McLoughlin <markmc@redhat.com> 0.132-1
- Update to 0.132
- Add rdesktop dependancy - see bug #114769

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Aug 29 2003 Jeremy Katz <katzj@redhat.com> 0.120-1
- 0.120

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu May  1 2003 Elliot Lee <sopwith@redhat.com> 0.104-2
- buildrequires: gnome-panel

* Wed Feb  5 2003 Havoc Pennington <hp@redhat.com> 0.104-1
- 0.104

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Fri Jan 10 2003 Havoc Pennington <hp@redhat.com>
- no word "applet" in the menus

* Wed Jan  8 2003 Jeff Johnson <jbj@redhat.com> 0.76-2
- don't include -debuginfo files in package.

* Mon Dec 16 2002 Havoc Pennington <hp@redhat.com>
- 0.76

* Sat Dec 14 2002 Havoc Pennington <hp@redhat.com>
- and 0.74 comes out mere hours later... ;-)

* Sat Dec 14 2002 Havoc Pennington <hp@redhat.com>
- 0.72
- fix description

* Thu Dec 12 2002 Havoc Pennington <hp@redhat.com>
- Initial build.
