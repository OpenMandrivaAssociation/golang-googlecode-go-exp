%if 0%{?fedora} || 0%{?rhel} == 6
%global with_devel 1
%global with_bundled 0
%global with_debug 0
%global with_check 1
%global with_unit_test 1
%else
%global with_devel 0
%global with_bundled 0
%global with_debug 0
%global with_check 0
%global with_unit_test 0
%endif

%if 0%{?with_debug}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%global provider        github
%global provider_tld    com
%global project         golang
%global repo            exp
# https://github.com/golang/exp
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     golang.org/x/exp
%global commit          d00e13ec443927751b2bd49e97dea7bf3b6a6487
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

%global gi_name         golang-%{provider}-%{project}-%{repo}
%global gc_import_path  code.google.com/p/go.exp

Name:           golang-googlecode-go-exp
Version:        0
Release:        0.18.git%{shortcommit}%{?dist}
Summary:        Experimental tools and packages for Go
License:        BSD
URL:            https://%{provider_prefix}
Source0:        https://%{provider_prefix}/archive/%{commit}/%{repo}-%{shortcommit}.tar.gz

# e.g. el6 has ppc64 arch without gcc-go, so EA tag is required
ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 %{arm}}
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}

%description
%{summary}

%if 0%{?with_devel}
%package devel
Summary:       %{summary}
BuildArch:     noarch

Provides:      golang(%{gc_import_path}/ebnf) = %{version}-%{release}
Provides:      golang(%{gc_import_path}/inotify) = %{version}-%{release}
Provides:      golang(%{gc_import_path}/old/netchan) = %{version}-%{release}
Provides:      golang(%{gc_import_path}/utf8string) = %{version}-%{release}
Provides:      golang(%{gc_import_path}/winfsnotify) = %{version}-%{release}

%description devel
%{summary}

This package contains library source intended for
building other packages which use import path with
%{gc_import_path} prefix.

%package -n %{gi_name}-devel
Summary:       %{summary}
BuildArch:     noarch

Provides:      golang(%{import_path}/ebnf) = %{version}-%{release}
Provides:      golang(%{import_path}/inotify) = %{version}-%{release}
Provides:      golang(%{import_path}/old/netchan) = %{version}-%{release}
Provides:      golang(%{import_path}/utf8string) = %{version}-%{release}
Provides:      golang(%{import_path}/winfsnotify) = %{version}-%{release}

%description -n %{gi_name}-devel
%{summary}

This package contains library source intended for
building other packages which use import path with
%{import_path} prefix.
%endif

%if 0%{?with_unit_test}
%package unit-test
Summary:         Unit tests for %{name} package

%if 0%{?with_check}
#Here comes all BuildRequires: PACKAGE the unit tests
#in %%check section need for running
%if 0%{?fedora} >= 23
BuildRequires:   golang-docs
%endif
%endif

# test subpackage tests code from devel subpackage
Requires:        %{gi_name}-devel = %{version}-%{release}
%if 0%{?fedora} >= 23
Requires:        golang-docs
%endif

%description unit-test
%{summary}

This package contains unit tests for project
providing packages with %{import_path} prefix.
%endif

%prep
%setup -q -n %{repo}-%{commit}

%build

%install
# source codes for building projects
%if 0%{?with_devel}
install -d -p %{buildroot}/%{gopath}/src/%{gc_import_path}/
echo "%%dir %%{gopath}/src/%%{gc_import_path}" >> gc_devel.file-list
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
echo "%%dir %%{gopath}/src/%%{import_path}" >> devel.file-list

# find all *.go but no *_test.go files and generate devel.file-list
for file in $(find . -iname "*.go" \! -iname "*_test.go") ; do
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    echo "%%dir %%{gopath}/src/%%{import_path}/$(dirname $file)" >> devel.file-list
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{gc_import_path}/$(dirname $file)
    echo "%%dir %%{gopath}/src/%%{gc_import_path}/$(dirname $file)" >> gc_devel.file-list
    cp -pav $file %{buildroot}/%{gopath}/src/%{gc_import_path}/$file
    echo "%%{gopath}/src/%%{gc_import_path}/$file" >> gc_devel.file-list
done
pushd %{buildroot}/%{gopath}/src/%{gc_import_path}/
# from https://groups.google.com/forum/#!topic/golang-nuts/eD8dh3T9yyA, first post
sed -i 's/"golang\.org\/x\//"code\.google\.com\/p\/go\./g' \
        $(find . -name '*.go')
popd
%endif

# testing files for this project
%if 0%{?with_unit_test}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
# find all *_test.go files and generate unit-test.file-list
for file in $(find . -iname "*_test.go"); do
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    echo "%%dir %%{gopath}/src/%%{import_path}/$(dirname $file)" >> devel.file-list
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> unit-test.file-list
done
%endif

%check
%if 0%{?with_check} && 0%{?with_unit_test} && 0%{?with_devel}
%if ! 0%{?with_bundled}
export GOPATH=%{buildroot}/%{gopath}:%{gopath}
%else
export GOPATH=%{buildroot}/%{gopath}:$(pwd)/Godeps/_workspace:%{gopath}
%endif

%if ! 0%{?gotest:1}
%global gotest go test
%endif

%gotest %{import_path}/ebnf
#%%gotest %{import_path}/ebnflint
# fails in arm
#%%gotest %%{import_path}/fsnotify
%gotest %{import_path}/inotify
%gotest %{import_path}/old/netchan
%gotest %{import_path}/utf8string
#%%gotest %%{import_path}/winfsnotify
%endif

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%if 0%{?with_devel}
%files devel -f gc_devel.file-list
%license LICENSE
%doc README AUTHORS CONTRIBUTORS PATENTS

%files -n %{gi_name}-devel -f devel.file-list
%license LICENSE
%doc README AUTHORS CONTRIBUTORS PATENTS
%endif

%if 0%{?with_unit_test}
%files unit-test -f unit-test.file-list
%license LICENSE
%doc README AUTHORS CONTRIBUTORS PATENTS
%endif

%changelog
* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.18.gitd00e13e
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.17.gitd00e13e
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.16.gitd00e13e
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.15.gitd00e13e
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Jun 26 2017 Jan Chaloupka <jchaloup@redhat.com> - 0-0.14.gitd00e13e
- Update Provided and [B]R packages
  related: #1250519

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.13.gitd00e13e
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Jul 21 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0-0.12.gitd00e13e
- https://fedoraproject.org/wiki/Changes/golang1.7

* Mon Apr 18 2016 jchaloup <jchaloup@redhat.com> - 0-0.11.gitd00e13e
- Bump to upstream d00e13ec443927751b2bd49e97dea7bf3b6a6487
  related: #1250519

* Mon Feb 22 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0-0.10.gite1eb486
- https://fedoraproject.org/wiki/Changes/golang1.6

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.9.gite1eb486
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Aug 20 2015 jchaloup <jchaloup@redhat.com> - 0-0.8.gite1eb486
- Choose the correct devel subpackage
  related: #1250519

* Thu Aug 20 2015 jchaloup <jchaloup@redhat.com> - 0-0.7.gite1eb486
- Fix %%files devel section
- Fix BR and R, change import path prefix to code.google.com/p
  related: #1250519

* Wed Aug 19 2015 jchaloup <jchaloup@redhat.com>
- Update spec file to spec-2.0
  resolves: #1250519

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0-0.5.hg77a5f324d8f5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue Dec 09 2014 jchaloup <jchaloup@redhat.com> - 0-0.4.hg77a5f324d8f5
- Update to the latest commit 77a5f324d8f52bc9a7116aab8ed7136f08ea5310
  related: #1148481

* Fri Nov 21 2014 jchaloup <jchaloup@redhat.com> - 0-0.3.hgbd8df7009305
- Extend import paths for golang.org/x/
  related: #1148481

* Sun Oct 26 2014 jchaloup <jchaloup@redhat.com> - 0-0.2.hgbd8df7009305
- Choose the correct architecture
  related: #1148481

* Mon Sep 15 2014 Eric Paris <eparis@redhat.com - 0-0.1.hgbd8df7009305
- Bump to upstream bd8df7009305d6ada223ea3c95b94c0f38bfa119
