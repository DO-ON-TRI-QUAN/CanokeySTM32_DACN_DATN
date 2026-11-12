# Install script for directory: C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "C:/Program Files (x86)/canokey")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "TRUE")
endif()

# Set path to fallback-tool for dependency-resolution.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "C:/ST/STM32CubeIDE_2.1.1/STM32CubeIDE/plugins/com.st.stm32cube.ide.mcu.externaltools.gnu-tools-for-stm32.14.3.rel1.win32_1.0.100.202602081740/tools/bin/arm-none-eabi-objdump.exe")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/mbedtls" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/aes.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/aesni.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/arc4.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/aria.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/asn1.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/asn1write.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/base64.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/bignum.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/blowfish.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/bn_mul.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/camellia.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/ccm.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/certs.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/chacha20.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/chachapoly.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/check_config.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/cipher.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/cipher_internal.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/cmac.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/compat-1.3.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/config.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/config_psa.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/ctr_drbg.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/debug.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/des.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/dhm.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/ecdh.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/ecdsa.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/ecjpake.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/ecp.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/ecp_internal.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/entropy.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/entropy_poll.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/error.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/gcm.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/havege.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/hkdf.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/hmac_drbg.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/md.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/md2.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/md4.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/md5.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/md_internal.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/memory_buffer_alloc.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/net.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/net_sockets.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/nist_kw.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/oid.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/padlock.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/pem.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/pk.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/pk_internal.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/pkcs11.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/pkcs12.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/pkcs5.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/platform.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/platform_time.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/platform_util.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/poly1305.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/psa_util.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/ripemd160.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/rsa.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/rsa_internal.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/sha1.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/sha256.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/sha512.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/ssl.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/ssl_cache.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/ssl_ciphersuites.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/ssl_cookie.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/ssl_internal.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/ssl_ticket.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/threading.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/timing.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/version.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/x509.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/x509_crl.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/x509_crt.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/x509_csr.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/mbedtls/xtea.h"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/psa" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/psa/crypto.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/psa/crypto_builtin_composites.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/psa/crypto_builtin_primitives.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/psa/crypto_compat.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/psa/crypto_config.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/psa/crypto_driver_common.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/psa/crypto_driver_contexts_composites.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/psa/crypto_driver_contexts_primitives.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/psa/crypto_extra.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/psa/crypto_platform.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/psa/crypto_se_driver.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/psa/crypto_sizes.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/psa/crypto_struct.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/psa/crypto_types.h"
    "C:/USB_Security_Token-DACN_DATN/CanokeySTM32_DACN_DATN/canokey-core/canokey-crypto/patched/mbedtls/include/psa/crypto_values.h"
    )
endif()

