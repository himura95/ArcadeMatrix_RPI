#[test]
fn test_version_endpoint_payload() {
    let version = env!("CARGO_PKG_VERSION");
    let target = env!("BUILD_TARGET");
    assert!(!version.is_empty());
    assert!(!target.is_empty());
}
