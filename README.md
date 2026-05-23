# Rotas-Gpx
Rotas das Linhas Carrismetropolitana 
endIconUrl:
                'https://cdn-icons-png.flaticon.com/512/149/149059.png',

                shadowUrl: ''
            }
        })

        .on('loaded', function(e){
            map.fitBounds(e.target.getBounds());
        })

        .addTo(map);
    };

    reader.readAsText(file);
});

</script>

</body>
</html>
