pluginManagement {
    // Kotlin 2.4 requires R8 >= 9.1.29; AGP 8.13 bundles an older reader.
    // https://developer.android.com/build/kotlin-support
    buildscript {
        repositories {
            maven {
                url = uri("https://storage.googleapis.com/r8-releases/raw")
                content { includeModule("com.android.tools", "r8") }
            }
            google()
            mavenCentral()
        }
        dependencies { classpath("com.android.tools:r8:9.1.29") }
    }

    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "yuvomi-android"
include(":app")
